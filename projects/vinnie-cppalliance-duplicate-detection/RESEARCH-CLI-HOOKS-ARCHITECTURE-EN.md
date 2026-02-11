# Research: CLI Comparison, Hooks & Architecture Analysis

**Date:** February 9, 2026  
**Author:** SG (Cursor Consultant)  
**Context:** C++ Alliance - AI Code Review Agent Project  
**Status:** Research Phase (Deadline: Mid-February 2026)

---

## Table of Contents

1. [Problem Analysis: Claude Code + GitHub Runner](#1-problem-analysis-claude-code--github-runner)
2. [Graphiti as Session Persistence Solution](#2-graphiti-as-session-persistence-solution)
3. [Deep Research: Cursor CLI vs Claude Code CLI](#3-deep-research-cursor-cli-vs-claude-code-cli)
4. [Hook Systems: Cursor vs Claude Code](#4-hook-systems-cursor-vs-claude-code)
5. [Webhook Server Architecture](#5-webhook-server-architecture)
6. [Agent Architecture: Swarm vs Multi-Agent vs Agent Teams](#6-agent-architecture-swarm-vs-multi-agent-vs-agent-teams)
7. [Webhook Server: How Do Agents Stay Active?](#7-webhook-server-how-do-agents-stay-active)
8. [Recommendation & Next Steps](#8-recommendation--next-steps)

---

## 1. Problem Analysis: Claude Code + GitHub Runner

### Current Architecture (from Huddle with Will Pak, Feb 3, 2026)

```
Human (GitHub UI)
    -> Issue Comment "@claude fix issue #188"
    -> GitHub Webhook triggered
    -> GitHub CI Workflow starts
        -> Runner allocated (Ubuntu VM)
        -> npm install claude-code          <-- Cold Start
        -> claude -p "fix this issue"
            -> Claude reads Issue, Code, etc.
            -> Claude creates PR, pushes commits
            -> CI Build runs (compilation, tests)
            -> If fails -> new commit -> CI again
            -> Up to 50 iterations              <-- Loop Problem
        -> Runner destroyed                     <-- State lost
```

### The 4 Pain Points and Their Root Causes

#### Pain Point 1: Slow Startup (2-5 Minutes)

**Root Cause: GitHub Actions Runner = Ephemeral VM**

On EVERY trigger:
1. GitHub must allocate a runner (30s - 2min queue time)
2. Fresh Ubuntu VM is started
3. Repository is cloned (for large C++ repos: 30s-2min)
4. `npm install claude-code` - Node.js runtime + dependencies (~300MB)
5. Claude Code initializes (context building, codebase scanning, API handshake)

**Result:** 2-5 minutes before the first token is generated.

#### Pain Point 2: Long CI Fix Loops (2h per iteration x 50 retries)

**Root Cause: C++ Compilation + Stateless Iterations**

A single iteration:
1. Claude pushes a fix commit (30s)
2. GitHub CI Workflow triggered
3. Runner allocation (1-2 min)
4. Dependencies installed (Boost, Clang = massive)
5. Project compilation (10-60 min)
6. Test matrix runs (10-30 min)
7. Result back to Claude

**Per iteration = 1-2 hours. At 50 retries = Multiple days.**

Made worse by: Claude has NO state from previous iterations. He doesn't know what he already tried and may attempt the same fix again.

#### Pain Point 3: No MCP in CI Runner

**Root Cause: Isolated Runtime Environment**

- LOCAL (works): Cursor -> MCP Server -> Pinecone Vector DB
- ON GITHUB RUNNER (missing): GitHub CI -> Claude Code -> ??? -> Pinecone

The CI agent that's supposed to fix Boost bugs has no access to the C++/Boost knowledge base that Will's team has built. It operates blind.

#### Pain Point 4: No Session Persistence

**Root Cause: CI Workflow = Fire-and-Forget**

```
Iteration 1: Claude learns "B2 Build Flag X breaks Test Y"
  -> VM destroyed -> Knowledge lost

Iteration 2: Claude learns the SAME thing again
  -> VM destroyed -> Knowledge lost

Iteration 3: Claude makes the SAME mistake as Iteration 1
```

### Core Problem in One Sentence

> They've squeezed a STATEFUL Agent (Claude Code) into a STATELESS environment (GitHub CI Runner) designed for short-lived build jobs, not long-lived iterative agent work.

---

## 2. Graphiti as Session Persistence Solution

### What is Graphiti?

[github.com/getzep/graphiti](https://github.com/getzep/graphiti) - An open-source framework for temporal knowledge graphs, developed by Zep. 22.6k GitHub Stars.

**Core features:**
- Real-Time Incremental Updates (no batch processing)
- Bi-Temporal Data Model (when did it happen + when was it recorded)
- Hybrid Retrieval (Semantic + Keyword + Graph Traversal)
- Custom Entity Definitions (Pydantic Models)
- MCP Server included

### Evaluation Against the 4 Pain Points

| Pain Point | Does Graphiti Solve It? | Assessment |
|---|---|---|
| **Slow Startup (2-5 min)** | NO | Graphiti needs its own DB (Neo4j/FalkorDB). Makes cold starts worse. |
| **Long CI Loops (~2h, 50 retries)** | Minimal | Theoretically fewer retries if agent remembers. But 2h CI runtime remains. |
| **No MCP for Pinecone** | NO (replacement, not connector) | Graphiti has MCP server but uses Neo4j/FalkorDB - NOT Pinecone. Migration needed. |
| **Session Persistence** | PARTIALLY | Semantic memory across sessions - yes. But no full session state. |

### Graphiti Conclusion

Graphiti solves only a fraction of the problem (semantic memory). The biggest pain points - cold start and CI runtime - are completely unaffected. Can serve as a **supplement**, but not as the primary solution.

---

## 3. Deep Research: Cursor CLI vs Claude Code CLI

### 3.1 Architecture & Philosophy

| Dimension | Cursor CLI (`cursor-agent`) | Claude Code (`claude`) |
|---|---|---|
| **Paradigm** | IDE extension as CLI | Terminal-first autonomous agent |
| **Models** | Multi-model: Claude 4.6 Opus, GPT-5.2, Gemini 3 Pro, Grok, Composer 1 | Anthropic-only: Sonnet 4.5, Opus 4.5/4.6, Haiku 4.5 |
| **Execution** | Local on your machine, no remote runner | Local OR remote (GitHub Actions Runner) |
| **Startup Time** | Instant - starts like any CLI process | 2-5 min cold start on CI runners |

### 3.2 Session Persistence

**Claude Code:**
- `claude --continue` - continue last conversation
- `claude --resume <id>` - resume specific session
- Full state is saved: Conversation History, Tool Calls, File References, Working Directory, Tool Permissions
- Background processes survive sessions
- `CLAUDE.md` + Auto-Memory load automatically (up to 200 lines)
- `.claude/rules/` for path-specific rules

**Cursor CLI:**
- `cursor-agent resume` - resume last session
- `cursor-agent --resume="chat-id"` - specific session
- `cursor-agent ls` - list all sessions
- Sessions stored in `~/.cursor/chats/`
- No automatic resume, manual chat-ID handling required
- Open Feature Request (#3846) for automatic session resume

**Verdict:** Claude Code wins clearly on session persistence.

### 3.3 MCP Support

**Claude Code:**
- Full MCP support: stdio, HTTP/SSE, Remote Servers
- Pre-built: PostgreSQL, GitHub, Slack, AWS, Puppeteer
- MCP Tool Search, MCP Prompts, MCP Resources

**Cursor CLI:**
- MCP support: stdio and SSE transport
- Same MCP stack as the Cursor Editor
- Access to Cursor's MCP Directory

**Verdict:** Both support MCP. For the Pinecone use case, you need a Pinecone MCP server either way.

### 3.4 CI/CD Integration

**Claude Code:**
- Official GitHub Action: `anthropics/claude-code-action` (5.5k stars)
- Known bugs: Exit Code 1 after 300-400ms, CPU leaks (100%+ idle), Orphaned Processes (running for days, $50-100 API costs)
- Cold start: npm install + runner allocation

**Cursor CLI:**
- GitHub Actions integration documented
- `cursor-agent -p "prompt" --output-format=text --force` for headless mode
- No dedicated runner needed - runs as normal CLI process
- Parallel Agents via Git Worktrees (up to 8)

**Verdict:** Cursor CLI has structural advantage on CI reliability.

### 3.5 Multi-Agent / Parallel Execution

**Claude Code:**
- Agent Teams (Opus 4.6): Multiple instances work collaboratively
- Task Tool: Built-in sub-agents with isolated contexts
- `.claude/agents/` for persistent specialists
- Max ~10 parallel sub-agents

**Cursor CLI:**
- Parallel Agents (Cursor 2.0): Up to 8 agents simultaneously
- Git Worktrees as isolation mechanism
- Subagents spawned via shell with `--model` flag
- Fan-out/Fan-in pattern

**Verdict:** Claude Code is more advanced in autonomous multi-agent coordination.

### 3.6 Pricing

| Plan | Cursor | Claude Code |
|---|---|---|
| **Free** | Hobby: 50 Premium Requests/month | No free tier |
| **$20/month** | Pro: $20 credit, all models | Pro: 45 msgs/5h, Sonnet 4.5 |
| **$60/month** | Pro+: Background Agents | - |
| **$100/month** | - | Max 5x: Opus 4.5 |
| **$200/month** | Ultra: 20x Usage | Max 20x: Priority Opus |
| **API** | $0.25/1M + model costs | Sonnet: $3/$15, Opus: $15/$75 per 1M |

**Token Efficiency:** Claude Code requires 5.5x fewer tokens for equivalent tasks (33k vs 188k).

### 3.7 Performance

| Metric | Cursor CLI | Claude Code |
|---|---|---|
| Autocomplete Speed | Sub-second | N/A |
| Refactoring Speed | 3-8 min (interactive) | 2-5 min (autonomous) |
| Token Efficiency | ~188k tokens/task | ~33k tokens/task |
| Context Window | 200k default, 1M Max | 200k default, 1M possible |
| Code Quality | No significant difference | No significant difference |

### 3.8 Security

**Claude Code:** OS-level sandboxing with gVisor-class isolation, filesystem + network isolation, 4 permission modes, 84% fewer permission prompts.

**Cursor CLI:** Shell mode with safety checks, "Security safeguards still evolving" (beta).

**Verdict:** Claude Code has the more mature security model.

### 3.9 Overall Assessment for C++ Alliance Use Case

| Pain Point | Cursor CLI | Claude Code | Winner |
|---|---|---|---|
| **Slow Startup** | Instant (local process) | 2-5 min on CI runners | **Cursor CLI** |
| **CI Fix Loops** | Headless mode, fast turnaround | Powerful but buggy | **Cursor CLI** |
| **MCP Support** | Full MCP support | Full MCP support | **Tie** |
| **Session Persistence** | Basic resume | Full state persistence | **Claude Code** |

---

## 4. Hook Systems: Cursor vs Claude Code

### 4.1 Overview

| Feature | Cursor Hooks | Claude Code Hooks |
|---|---|---|
| **Config File** | `.cursor/hooks.json` | `.claude/settings.json` |
| **Hook Types** | 1 type: Command | 3 types: Command, Prompt, Agent |
| **Number of Events** | ~8 events | 15 events |
| **Blocking** | Partial | Full control (Exit Codes + JSON) |
| **MCP Hooks** | No | Yes (`mcp__server__tool` matcher) |
| **Async/Background** | No | Yes (`async: true`) |
| **Subagent Hooks** | No | Yes (`SubagentStart`, `SubagentStop`) |
| **Agent Teams** | N/A | `TeammateIdle`, `TaskCompleted` |
| **Interactive Menu** | No | `/hooks` command |

### 4.2 Claude Code: All 15 Hook Events

```
SESSION LIFECYCLE:
+-- SessionStart         -> Session begins/resumed
+-- SessionEnd           -> Session ends
+-- PreCompact           -> Before context compaction

USER INTERACTION:
+-- UserPromptSubmit     -> Before prompt is processed

TOOL LIFECYCLE:
+-- PreToolUse           -> BEFORE tool execution (can BLOCK)
+-- PermissionRequest    -> At permission dialog
+-- PostToolUse          -> AFTER successful tool execution
+-- PostToolUseFailure   -> AFTER failed tool execution

AGENT LIFECYCLE:
+-- SubagentStart        -> Subagent is spawned
+-- SubagentStop         -> Subagent finished
+-- Stop                 -> Claude stops responding
+-- TeammateIdle         -> Agent team member going idle
+-- TaskCompleted        -> Task being marked as completed

NOTIFICATIONS:
+-- Notification         -> Claude sends notification
```

### 4.3 The 3 Hook Types in Claude Code

#### Command Hook (also available in Cursor)
Shell script receiving JSON via stdin:
```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Write|Edit",
      "hooks": [{ "type": "command", "command": ".claude/hooks/format.sh" }]
    }]
  }
}
```

#### Prompt Hook (Claude Code only)
An LLM evaluates whether the action is allowed:
```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "prompt",
        "prompt": "Is this command safe? $ARGUMENTS"
      }]
    }]
  }
}
```

#### Agent Hook (Claude Code only)
A full subagent with tools (Read, Grep, Glob) is spawned:
```json
{
  "hooks": {
    "Stop": [{
      "hooks": [{
        "type": "agent",
        "prompt": "Check if all tests pass and code is formatted. $ARGUMENTS"
      }]
    }]
  }
}
```

### 4.4 Exit Code System

- `Exit 0` = Allow action (optional JSON output)
- `Exit 2` = BLOCK action (stderr is shown to Claude as error)
- `Other Exit` = Non-blocking error

### 4.5 Relevance for C++ Alliance

| Hook | Use Case |
|---|---|
| `SessionStart` | Auto-connect MCP/Pinecone, load git status |
| `PreToolUse` + Bash | Block dangerous commands (`rm -rf`, `git push --force`) |
| `PostToolUse` + Edit | Auto-formatter (clang-format) after file changes |
| `Stop` (Agent Hook) | Review agent checks if tests pass BEFORE Claude says "done" |
| `SubagentStop` | Validate results of parallel agents |
| `TaskCompleted` | Prevent task from being marked "done" without CI success |

**Critical insight:** The `Stop` hook with agent type prevents Claude from declaring "done" until a subagent confirms tests are passing. This drastically reduces the 50-retry loops.

---

## 5. Webhook Server Architecture

### What is a Webhook Server?

A dedicated server on the internet that listens for HTTP requests. With GitHub Webhooks:

1. GitHub sends HTTP POST to your server URL when events occur (Issue, PR, CI failure)
2. Server receives and validates signature (security)
3. Server executes action (e.g., starts Claude Code)

### Why This Solves the Problems

| Problem | GitHub CI Runner | Webhook Server |
|---|---|---|
| Cold Start | 2-5 min (VM + npm install) | Instant (process running permanently) |
| State | Lost after every run | Persistent (server stays alive) |
| MCP | Must be installed per run | Runs permanently alongside agent |
| Build Cache | Limited (GitHub Cache Actions) | Full local cache |

### Architecture

```
GitHub Repository
    |
    v (Webhook: issue_comment, pull_request, check_run)
    |
Webhook Server (Hetzner/AWS/etc.)
    |
    +-- Express.js/FastAPI (receives events)
    +-- Claude Code SDK (running permanently)
    +-- MCP Server (Pinecone connection)
    +-- Self-hosted Runner (local builds)
    +-- Build Cache (Boost, Clang pre-built)
```

### Advantages Over Current Architecture

- **Instant Response**: Agent responds in seconds, not minutes
- **Session Persistence**: `claude --continue` works because the process is alive
- **MCP Always Available**: Pinecone knowledge base permanently connected
- **Build Cache**: Boost/Clang pre-built, only delta compilation
- **Cost Control**: No runner-minute consumption on GitHub

---

## 6. Agent Architecture: Swarm vs Multi-Agent vs Agent Teams

### 6.1 The Three Paradigms

#### Swarm (OpenAI-style)
- Many identical agents that self-organize
- No fixed leader, emergent coordination
- Good for: homogeneous tasks (e.g. reviewing 100 PRs in parallel)
- Bad for: complex workflows with different roles

#### Multi-Agent / Subagents (Claude Code built-in)
- One main agent spawns specialized sub-agents
- Sub-agents report back to the main agent
- Own context per sub-agent, result is summarized
- Good for: focused tasks where only the result matters
- Token cost: Low (result summarized back)

#### Agent Teams (Claude Code, new with Opus 4.6)
- One lead coordinates independent teammates
- Teammates communicate DIRECTLY with each other (peer-to-peer)
- Shared task list with self-coordination
- Good for: complex work requiring discussion and collaboration
- Token cost: HIGH (each teammate = separate Claude instance)

### 6.2 Reference Architecture: Atomic.Net Manager Pattern

Source: [github.com/SteffenBlake/Atomic.Net](https://raw.githubusercontent.com/SteffenBlake/Atomic.Net/refs/heads/main/.github/agents/manager.agent.md)

**Core Principle: The Manager NEVER codes itself. It ONLY delegates.**

```
Manager Agent (Orchestrator)
    |
    |-- FORBIDDEN: calling explore, task, or any other agents
    |-- ONLY JOB: Delegate to the 5 specialized agents
    |
    +-- tech-lead
    |   Role: Convert requirements from issues -> sprint files
    |   Trigger: Only when explicitly requested
    |   Output: Sprint file (must be human-reviewed)
    |
    +-- senior-dev
    |   Role: Implementation, bug fixes, test repair
    |   Trigger: After sprint file approval or direct bug requests
    |   Output: Code changes
    |
    +-- benchmarker
    |   Role: Create and run performance benchmarks
    |   Trigger: Only on explicit request
    |   Output: Benchmark results
    |
    +-- profiler
    |   Role: Profiling and tracing of specific code sections
    |   Trigger: Only on explicit request
    |   Output: Performance analysis
    |
    +-- code-reviewer
        Role: Extensive code review of EVERY change
        Trigger: AFTER every "developer" agent's work
        Output: Review with feedback or "100% ALL CLEAR"
```

**Critical Rules:**
1. Code-reviewer activates AFTER EVERY change
2. On ANY feedback (no matter how small) -> back to developer
3. Loop ends ONLY when: ALL tests pass AND review = 100% ALL CLEAR
4. NO time limits - agent uses 100% of its token limit
5. Work is NOT done until everything is green

### 6.3 Translation to Claude Code Architecture

#### Option A: Subagents (simpler, cheaper)

```json
// .claude/agents/manager.md
---
name: manager
description: Orchestrates specialized agents for C++ Alliance
tools: ['custom-agent']
---

YOUR ONLY JOB: Delegate to these agents:
1. knowledge-agent: Queries MCP/Pinecone for C++ Boost context
2. coding-agent: Implements fixes based on knowledge + issue
3. review-agent: Reviews EVERY fix for correctness

WORKFLOW:
1. Issue comes in -> knowledge-agent fetches relevant context
2. coding-agent receives context + issue -> implements fix
3. review-agent checks the fix
4. On feedback -> back to coding-agent
5. Loop until review-agent gives "ALL CLEAR"
6. ONLY THEN: Push and create PR
```

#### Option B: Agent Teams (powerful, expensive)

```
Lead Agent (Manager)
    |
    +-- Teammate: knowledge-researcher
    |   - Queries Pinecone via MCP
    |   - Finds similar issues/fixes
    |   - Communicates directly with coding-dev
    |
    +-- Teammate: coding-dev
    |   - Implements fixes
    |   - Gets context from knowledge-researcher
    |   - Gets challenged by code-reviewer
    |
    +-- Teammate: code-reviewer
        - Reviews ALL changes
        - Challenges coding-dev directly
        - Only clears when everything is clean
```

### 6.4 Recommendation for C++ Alliance

**START with Subagents (Option A):**
- Simpler to set up
- Cheaper token costs
- Sufficient for the MVP
- 3 agents: knowledge, coding, review

**LATER upgrade to Agent Teams (Option B) when:**
- Subagents hit limitations (e.g. coding-agent needs to ask knowledge-agent questions during work)
- Budget for higher token costs is available
- More complex tasks requiring peer-to-peer communication

---

## 7. Webhook Server: How Do Agents Stay Active?

### 7.1 The Answer: Agents Are NOT 24/7 Active

**Claude Code is NOT a daemon.** It's a CLI process that starts, works, and exits.

**BUT: The webhook server IS 24/7 active.**

The architecture is like a doctor on-call:
- The server is 24/7 REACHABLE (Express/FastAPI process)
- Claude Code is spawned ON-DEMAND when a webhook arrives
- Sessions are restored with `--continue`/`--resume`
- MCP server runs permanently as a separate process

### 7.2 Architecture Diagram

```
                    PERMANENTLY RUNNING (24/7)
                    ==========================
                    
GitHub --webhook--> Webhook Server (FastAPI/Express)
                         |
                         +-- MCP Server (Pinecone) [permanent]
                         +-- Build Cache (Boost/Clang) [on disk]
                         +-- Session Store (~/.claude/) [persistent]
                         
                    STARTED ON-DEMAND (per event)
                    =============================
                    
                    Webhook received
                         |
                         v
                    claude -p "Fix issue #188" \
                      --continue \
                      --allowedTools "Read,Edit,Bash" \
                      --output-format json
                         |
                         +-- Subagent: knowledge (queries MCP)
                         +-- Subagent: coding (implements)
                         +-- Subagent: review (checks)
                         |
                         v
                    Result -> GitHub API -> PR/Comment
                    
                    Claude process exits
                    Session state remains in ~/.claude/
```

### 7.3 Pseudocode: Webhook Server

```python
# server.py (FastAPI - runs 24/7)
from fastapi import FastAPI, Request
import subprocess
import json
import hmac

app = FastAPI()
WEBHOOK_SECRET = os.environ["GITHUB_WEBHOOK_SECRET"]
SESSION_MAP = {}  # issue_id -> claude session_id

@app.post("/webhook")
async def handle_webhook(request: Request):
    # 1. Validate signature
    payload = await request.body()
    signature = request.headers.get("X-Hub-Signature-256")
    verify_signature(payload, signature, WEBHOOK_SECRET)
    
    data = json.loads(payload)
    action = data.get("action")
    
    # 2. Determine event type
    if "issue" in data and action == "opened":
        await handle_new_issue(data)
    elif "check_run" in data and data["check_run"]["conclusion"] == "failure":
        await handle_ci_failure(data)

async def handle_new_issue(data):
    issue_id = data["issue"]["number"]
    repo = data["repository"]["full_name"]
    
    # 3. Spawn Claude Code with session resume
    cmd = [
        "claude", "-p",
        f"Fix issue #{issue_id} in {repo}. "
        f"Use the MCP server to query Pinecone for relevant C++ context. "
        f"Create a PR with the fix.",
        "--allowedTools", "Read,Edit,Bash,mcp__pinecone__query",
        "--output-format", "json"
    ]
    
    # Resume if session exists
    if issue_id in SESSION_MAP:
        cmd.extend(["--resume", SESSION_MAP[issue_id]])
    
    # 4. Execute
    result = subprocess.run(cmd, capture_output=True, text=True)
    output = json.loads(result.stdout)
    
    # 5. Save session ID for next time
    SESSION_MAP[issue_id] = output["session_id"]
    
    # 6. Post result to GitHub
    post_github_comment(repo, issue_id, output["result"])

async def handle_ci_failure(data):
    run_id = data["check_run"]["id"]
    repo = data["repository"]["full_name"]
    
    cmd = [
        "claude", "-p",
        f"CI run {run_id} failed. Analyze the error and push a fix. "
        f"Query Pinecone for similar past failures.",
        "--continue",  # Continue last session
        "--allowedTools", "Read,Edit,Bash,mcp__pinecone__query",
        "--output-format", "json"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    # ... process result
```

### 7.4 What Runs Permanently vs. On-Demand

| Component | Runtime | Cost |
|---|---|---|
| **FastAPI Server** | 24/7 | ~$5-20/month (Hetzner VPS) |
| **MCP Server (Pinecone)** | 24/7 | Minimal (lightweight process) |
| **Build Cache** | On Disk | One-time creation |
| **Claude Code Process** | On-demand (minutes per event) | API token costs per invocation |
| **Subagents** | On-demand (within Claude) | Part of token costs |

**Result: The 24/7 costs are minimal (~$5-20/month server). Actual costs only arise when Claude is working (token-based).**

---

## 8. Recommendation & Next Steps

### Short-Term Recommendation (MVP by Mid-February)

1. **Set up webhook server** (FastAPI on Hetzner VPS)
2. **Claude Code with subagents** (3 agents: knowledge, coding, review)
3. **MCP Server for Pinecone** permanently on the server
4. **Hook system:**
   - `Stop` Hook: Review agent must give "ALL CLEAR"
   - `PreToolUse` Hook: Block dangerous commands
   - `SessionStart` Hook: Auto-load context
5. **Session resume** for state persistence between iterations

### Mid-Term Recommendation

- Upgrade to Agent Teams when subagents become limiting
- Self-hosted runner for local C++ builds
- Build cache for Boost/Clang

### Long-Term Recommendation

- Hybrid: Cursor CLI for fast checks + Claude Code Agent Teams for complex tasks
- AutoAgent GitHub Action for both CLIs in one pipeline
- Graphiti or similar for long-term project memory (optional)

### Open Questions for Mid-February Meeting

1. Budget for webhook server infrastructure (Hetzner vs AWS)?
2. Which Pinecone MCP server will be used (custom or existing)?
3. Should Cursor CLI be evaluated in parallel with Claude Code?
4. How will the build cache for Boost/Clang be managed (S3, local)?
5. How many parallel agents should run (cost vs speed)?
6. Agent Teams (experimental) vs Subagents (stable) - what risk level?
7. Manager pattern like Atomic.Net or simpler approach?

---

**Sources:**
- Huddle Transcript: Will Pak & SG, February 3, 2026
- [github.com/getzep/graphiti](https://github.com/getzep/graphiti)
- [docs.cursor.com/cli](https://docs.cursor.com/en/cli/overview)
- [code.claude.com/docs/en/hooks](https://code.claude.com/docs/en/hooks)
- [code.claude.com/docs/en/agent-teams](https://code.claude.com/docs/en/agent-teams)
- [code.claude.com/docs/en/headless](https://code.claude.com/docs/en/headless) (SDK/Programmatic Usage)
- [Atomic.Net Manager Agent](https://raw.githubusercontent.com/SteffenBlake/Atomic.Net/refs/heads/main/.github/agents/manager.agent.md)
- [cursor.com/cli](https://cursor.com/cli)
- [anthropics/claude-code-action](https://github.com/anthropics/claude-code-action)
- Various web research (Feb 2026)
