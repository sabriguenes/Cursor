# Architecture Decisions: Questions & Answers

**Document Type:** Internal Q&A Reference  
**Date:** February 10, 2026  
**Context:** Multi-Agent Code Review System for LLVM/Clang  
**Version:** 2.0 (Updated: Built-in Orchestration Architecture)

---

## Q1: Why Claude Code and not Cursor CLI?

**Short answer:** Claude Code has built-in subagent orchestration (`.claude/agents/` Markdown definitions), 15 hook events, and native MCP routing per agent. Cursor CLI has none of these.

**Important correction:** Cursor CLI does **not** perform codebase indexing — only the Cursor IDE does (source: official Cursor docs, `docs.cursor.com/context/codebase-indexing`, confirmed by Cursor team member Tee on Discord). Both CLIs work file-based (Read, Grep, Glob) without an index. The 2–5 minute delay in the current setup comes from **GitHub Runner allocation + npm install**, not from any CLI indexing.

**The actual differentiators:**

| Capability | Cursor CLI (`cursor-agent`) | Claude Code CLI | Winner |
|------------|---------------------------|------------------------|--------|
| Codebase indexing | No (IDE-only feature) | No | Tie |
| How it finds code | File-based (Read, Grep, Glob) | File-based (Read, Grep, Glob) | Tie |
| Session persistence | `--resume` (Beta) | `--resume` + `--continue` | Claude Code |
| MCP support | Yes (via `mcp.json`) | Yes (native, per-agent routing) | Claude Code |
| Built-in Subagents | Not available | `.claude/agents/*.md` with model/tool/MCP config | **Claude Code** |
| Agent Teams (experimental) | Not available | Peer-to-peer multi-agent orchestration | **Claude Code** |
| Hook system | 8 events (IDE-only) | 15 events (CLI-compatible) | **Claude Code** |
| Headless / CI mode | Limited | Full support with `--output-format json` | **Claude Code** |
| Multi-model support | GPT-5, Claude, Gemini, Grok | Anthropic-only (Haiku, Sonnet, Opus) | Cursor CLI |

**Bottom line:** The decision for Claude Code is based on three capabilities Cursor CLI lacks entirely:

1. **Built-in Subagents** — agents defined as Markdown files (`.claude/agents/*.md`) with per-agent model selection, tool restrictions, and MCP server routing
2. **Agent Teams** — experimental peer-to-peer orchestration for future upgrade path
3. **15 Hook Events** — `PreToolUse`, `PostToolUse`, `SessionStart`, `SubagentStart`, `SubagentStop`, etc., all functional in headless mode

Cursor CLI is an excellent tool for interactive development, but it lacks the native multi-agent orchestration layer we need for a webhook-driven system.

**Sources:**
- Cursor Docs: `docs.cursor.com/context/codebase-indexing` — "Cursor indexes your codebase... When you open a project" (IDE feature)
- Cursor CLI Docs: `docs.cursor.com/en/cli/overview` — no mention of indexing
- Discord confirmation: Tee (Cursor team) — "Cursor CLI does not index codebase, this is only done by the IDE"
- Claude Code Subagents: `docs.anthropic.com/docs/en/sub-agents` — custom agent definitions via `.claude/agents/`
- Claude Code Agent Teams: `code.claude.com/docs/en/agent-teams` — multi-agent team orchestration
- Claude Code Hooks: `code.claude.com/docs/en/hooks-guide` — 15 event types

---

## Q2: Can every developer hit the webhook server with their Claude Code?

**Short answer:** Yes. Any developer with push access to the GitHub repo automatically triggers the webhook server. No local Claude Code installation required.

**How it works:**

```
Developer pushes code / creates PR / comments on issue
    |
    v
GitHub fires a webhook (HTTP POST) to our FastAPI server
    |
    v
FastAPI server receives the event, validates the signature
    |
    v
Server spawns Claude Code with built-in subagents (--agent orchestrator)
    |
    v
Agent works, posts result back to GitHub as a comment/review
```

**Key points:**

- **No local setup required** — developers interact only with GitHub, the server handles everything
- **Single `ANTHROPIC_API_KEY`** — managed centrally on the server, not per-developer
- **Token costs tracked per agent run** — visible in the monitoring dashboard
- **Optional direct access** — the dashboard can expose a manual trigger endpoint for ad-hoc agent requests outside of GitHub events
- **Access control** — GitHub webhook signatures ensure only legitimate events are processed; the server rejects forged requests

**Who can trigger it:**
- Anyone who can create issues, PRs, or comments on the monitored GitHub repo
- The webhook server validates the GitHub signature secret — no unauthorized access possible

---

## Q3: Does it run 24/7?

**Short answer:** The **server** runs 24/7. The **agents** run on-demand.

**What runs permanently (24/7):**

| Component | Runtime | Monthly Cost |
|-----------|---------|-------------|
| FastAPI webhook server | 24/7 (systemd service) | $0 (on Azure VM) |
| MCP server (Pinecone connection) | 24/7 (systemd service) | $0 (on Azure VM) |
| SQLite database | 24/7 (file on disk) | $0 |
| nginx reverse proxy | 24/7 (HTTPS termination) | $0 |
| Azure VM (B2ms, Ubuntu 22.04) | 24/7 | ~$60/month (MS credits) |

**What runs on-demand (event-triggered):**

| Component | Trigger | Duration | Cost |
|-----------|---------|----------|------|
| Knowledge Agent | GitHub event arrives | Seconds | ~$0.01–0.05 |
| Coding Agent | Knowledge agent returns context | Minutes | ~$0.50–2.00 |
| Review Agent | Coding agent completes changes | Seconds–minutes | ~$0.10–0.30 |

**Analogy:** A doctor on call — not operating 24/7, but reachable 24/7. The server is the hospital that never closes. The agents are the specialists called in when needed.

**Reliability:**
- `systemd` ensures auto-restart if the FastAPI server crashes
- Health check endpoint (`/health`) for external monitoring
- Azure VM uptime SLA: 99.9%
- If the VM goes down, GitHub webhooks queue and retry automatically (GitHub retries failed webhook deliveries)

---

## Q4: Is it cost-efficient (as much as possible)?

**Short answer:** Yes, through three cost levers: hybrid LLM strategy, on-demand spawning, and Microsoft startup credits.

**Lever 1: Hybrid LLM Strategy (right model for the right task)**

| Agent | Model | Why This Model | Cost per Invocation |
|-------|-------|---------------|-------------------|
| Knowledge Agent | Sonnet 4 | Simple retrieval task, no code generation | ~$0.01–0.05 (cheapest) |
| Coding Agent | Opus 4.6 | C++ code quality demands the best model | ~$0.50–2.00 (most expensive) |
| Review Agent | Sonnet 4 | Review requires quality but fewer tokens | ~$0.10–0.30 (medium) |

**The cost gradient works naturally:** The knowledge agent runs most frequently (every event) but is the cheapest. The expensive coding agent only runs when actual code changes are needed — not for every webhook.

**Lever 2: On-demand spawning (no idle agent costs)**

- Agents are spawned per-event, not running continuously
- Zero API cost when no GitHub events arrive
- No wasted tokens on idle processes
- `max_budget_usd` parameter prevents token overruns per agent invocation

**Lever 3: Microsoft startup credits ($5,000)**

| Component | Monthly Cost | Covered By | Runway |
|-----------|-------------|-----------|--------|
| Azure VM (B2ms) | ~$60 | MS credits | 83 months |
| Azure Blob Storage | ~$5 | MS credits | — |
| Azure Key Vault | ~$1 | MS credits | — |
| **Total infrastructure** | **~$66/month** | **MS credits** | **76+ months** |

**Comparison with alternatives:**

| Approach | Monthly Cost | Why More Expensive |
|----------|------------|-------------------|
| Our architecture | ~$66 + API tokens | Minimal infrastructure, on-demand agents |
| GitHub Runners (current) | $0 infra + API tokens + wasted dev time | Free infra but 2-5 min per interaction = expensive in developer hours |
| Full LangGraph/CrewAI stack | ~$200+ + API tokens | Additional SaaS fees, complexity overhead |

---

## Q5: Is a token/prompt strategy defined?

**Short answer:** Yes. Every agent has scoped prompts, restricted tools, turn limits, and budget caps.

**Strategy layer 1: Scoped system prompts**

Each agent receives ONLY the instructions relevant to its role. No agent sees the full system context. This minimizes token consumption per invocation:

- **Knowledge Agent prompt:** "Query Pinecone and SQLite. Return structured context. DO NOT write code."
- **Coding Agent prompt:** "Implement changes based on context. Clean diffs. Clear commits."
- **Review Agent prompt:** "Review changes. Respond 'ALL CLEAR' or return specific feedback."

**Strategy layer 2: Tool restrictions**

| Agent | Allowed Tools | Forbidden |
|-------|--------------|-----------|
| Knowledge Agent | Read, Grep, Glob, MCP | Edit, Write, Bash, Git |
| Coding Agent | Read, Edit, Write, Bash, Grep, Glob | — (full access) |
| Review Agent | Read, Grep, Glob, Bash (tests only) | Edit, Write |

The orchestrator itself has **no coding tools** (Atomic.Net Manager Pattern: "YOUR ONLY JOB IS TO DELEGATE").

**Strategy layer 3: Execution limits**

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `max_turns` per agent | 10–20 (configurable) | Prevent infinite loops |
| `max_budget_usd` per agent | $2.00 (configurable) | Hard cost ceiling per invocation |
| Review loop iterations | Max 3 | Prevent endless coding ↔ review cycles |
| Context window management | Each agent starts fresh | No accumulated context bloat across agents |

**Strategy layer 4: Context passing (not context sharing)**

Agents don't share a context window. Instead, the orchestrator passes **summarized results** between agents:

```
Knowledge Agent → returns: structured context summary (500-1000 tokens)
    |
    v (only the summary is passed, not the full retrieval)
Coding Agent → returns: list of changed files + diff (variable)
    |
    v (only the diff is passed, not the full codebase context)
Review Agent → returns: "ALL CLEAR" or specific feedback (100-500 tokens)
```

This means each agent operates within its own context window, never inheriting bloated context from a previous agent. Token efficiency is maximized by design.

---

## Q6: Are there clearly defined, professionally specialized agent roles?

**Short answer:** Yes. 3 specialized agents + 1 orchestrator, each with strict role boundaries, scoped tools, and dedicated model selection.

**The four roles:**

| Role | Specialization | Tools | Model | Cost Tier |
|------|---------------|-------|-------|-----------|
| **Orchestrator** | Delegates ONLY, codes NEVER | No coding tools | FastAPI logic (deterministic) | $0 (no LLM) |
| **Knowledge Agent** | C++ knowledge retrieval from Pinecone + SQLite | Read, Grep, Glob, MCP | Sonnet 4 | LOW |
| **Coding Agent** | Senior C++ developer — implements fixes, creates PRs | Read, Edit, Write, Bash, Git, Grep, Glob | Opus 4.6 | HIGH |
| **Review Agent** | Code reviewer — validates every change before PR creation | Read, Grep, Glob, Bash (tests) | Sonnet 4 | MEDIUM |

**Role boundaries are enforced, not suggested:**

The orchestrator follows the Atomic.Net Manager Pattern:

> *"CRITICAL: YOU ARE FORBIDDEN FROM CALLING AGENTS OTHER THAN THE ONES LISTED. Your ONLY job is to delegate to these agents. THAT'S IT."*
> — Adapted from [SteffenBlake/Atomic.Net manager.agent.md](https://github.com/SteffenBlake/Atomic.Net)

**Why these specific roles?**

Each role maps to a distinct phase in the code review pipeline:

```
GitHub Event
    |
    v
[1] KNOWLEDGE AGENT  — "What does the C++ community say about this pattern?"
    |                    Queries Pinecone for similar review comments.
    |                    Queries SQLite for reviewer statistics.
    |                    Returns: structured context (no code changes).
    v
[2] CODING AGENT     — "Implement the fix based on this context."
    |                    Receives context from Knowledge Agent.
    |                    Writes code, creates clean diffs.
    |                    Returns: changed files + commit message.
    v
[3] REVIEW AGENT     — "Is this code correct and complete?"
    |                    Reviews the Coding Agent's work.
    |                    Runs tests if available.
    |                    Returns: "ALL CLEAR" or "FEEDBACK: [specific issues]"
    |
    +---> ALL CLEAR? ---> Create PR on GitHub
    |
    +---> FEEDBACK? ---> Back to Coding Agent (max 3 iterations)
```

**Professional specialization:**

- The **Knowledge Agent** is like a research librarian — it finds relevant information but never writes the paper
- The **Coding Agent** is like a senior developer — it writes the code but doesn't review its own work
- The **Review Agent** is like a code reviewer / QA engineer — it validates but never implements
- The **Orchestrator** is like a project manager — it coordinates but never codes

This separation prevents the "single agent doing everything" antipattern that degrades quality as context grows.

**Upgrade path:**

If future requirements demand more specialization, additional agents can be added without changing the pipeline:

- **CI-Fixer Agent** — responds to `check_run` failures, fixes build errors
- **Documentation Agent** — generates/updates docs when code changes
- **Security Agent** — scans changes for vulnerabilities before PR creation

The architecture is designed to scale horizontally by adding agents, not by making existing agents more complex.

---

## Appendix: Correction Notice

**Previous incorrect statement (verbal, not in documents):**

> ~~"Cursor CLI re-indexes the codebase on every run, causing 2-5 minute cold starts"~~

**Corrected statement:**

Cursor CLI does **not** perform codebase indexing. Indexing is exclusively an IDE feature (`docs.cursor.com/context/codebase-indexing`). Both Cursor CLI and Claude Code CLI work file-based without an index. The 2-5 minute delay in the C++ Alliance's current setup is caused by **GitHub Runner VM allocation and npm install**, not by any CLI indexing behavior.

The decision for Claude Code over Cursor CLI is based on:
1. Built-in subagents (`.claude/agents/*.md`) with per-agent model/tool/MCP configuration
2. Agent Teams for future upgrade path to peer-to-peer orchestration
3. 15 hook events functional in headless/CI mode (vs 8 IDE-only events in Cursor)

Not on indexing performance.

---

*Prepared: February 10, 2026*  
*Reference documents: CONSULTANT-PAPER-AGENT-ARCHITECTURE.md, PROJECT-PLAN.md, RESEARCH-CLI-HOOKS-ARCHITECTURE-EN.md*
