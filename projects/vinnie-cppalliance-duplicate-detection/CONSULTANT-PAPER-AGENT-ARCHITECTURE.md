# Technical Architecture Proposal: Multi-Agent Code Review System for LLVM/Clang

**Prepared for:** C++ Alliance — Vinnie Falco, Will Pak  
**Prepared by:** SG Consulting  
**Date:** February 10, 2026  
**Document Type:** Technical Architecture Recommendation  
**Classification:** Client-Facing Deliverable  
**Version:** 2.0 (Updated: Built-in Orchestration Architecture)

---

## Executive Summary

**Recommendation:** Deploy a multi-agent orchestration system using **Claude Code's built-in subagent system** (`.claude/agents/` Markdown definitions) with a **FastAPI webhook server**, backed by a **Database-First Knowledge Pipeline** with built-in data integrity verification. This architecture eliminates the 2–5 minute cold-start problem, enables real-time GitHub integration, and provides full observability through a live monitoring dashboard.

**Key outcomes this architecture delivers:**

| Outcome | Current State | Proposed State |
|---------|--------------|----------------|
| Response time | 2–5 min cold start on GitHub Runners | < 10 sec webhook-to-agent |
| Agent coordination | Single agent, no orchestration | 3 specialized agents with pipeline routing |
| Knowledge access | Manual context, no persistence | Instant SQLite + Pinecone queries with verified data integrity |
| Observability | None — black box | Real-time dashboard with logs, costs, and agent steps |
| Session continuity | Every run starts from scratch | Persistent sessions with state resume |

**Estimated infrastructure cost:** ~$65/month on Azure (covered by existing $5,000 Microsoft startup credits for 76+ months of runway).

---

## 1. Situation

The C++ Alliance maintains an AI-assisted code review workflow for LLVM/Clang repositories. The current system uses Claude Code on GitHub Runners with a Pinecone-backed MCP server containing C++ and Boost reference knowledge. A proof-of-concept agent ("Cappy") can pull data, request commits, and suggest fixes.

**What works today:**
- Claude Agent on GitHub — functional, can interact with repos
- MCP Package — published, connected to Claude Code
- Vector Database — populated with C++ and Boost high-quality data
- Data Pipeline — partially built (JSON format, needs MD conversion)

---

## 2. Complication

Five critical bottlenecks prevent the current system from scaling to production use:

| # | Problem | Impact | Root Cause |
|---|---------|--------|------------|
| 1 | **Slow startup** | 2–5 min until agent responds | GitHub Runner allocation + npm install on every invocation |
| 2 | **Long iteration cycles** | ~2h per CI fix attempt, up to 50 retries/day | No session persistence, agent restarts from scratch each time |
| 3 | **No orchestration** | Single agent handles all tasks | No role separation, context window bloats with mixed concerns |
| 4 | **No observability** | Cannot monitor what agents are doing | No logging, no dashboard, no cost tracking |
| 5 | **No data integrity** | Unknown data loss in pipeline | No verification that scraped data == indexed data == embedded data |

**Business impact:** Developer time is wasted waiting for agents. The feedback loop is measured in hours, not seconds. Without orchestration, the agent's quality degrades as context grows. Without observability, debugging is guesswork.

---

## 3. Resolution: Proposed Architecture

### 3.1 Architecture Overview

We propose a four-layer architecture that maps to proven patterns from both the consulting industry's reference frameworks (OpenAI's Agent Guide, Deloitte's Agentic Enterprise) and a battle-tested open-source static analysis tool (TheAuditor v2, AGPL-3.0):

```
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 1: EXPERIENCE                                                │
│  Agent Dashboard (HTMX + WebSocket)                                │
│  Live logs, agent status, cost tracking, step visualization         │
├─────────────────────────────────────────────────────────────────────┤
│  LAYER 2: ORCHESTRATION                                             │
│  FastAPI Webhook Server + Claude Code CLI (Built-in Subagents)    │
│  Event routing, agent delegation, review loops, session management │
├─────────────────────────────────────────────────────────────────────┤
│  LAYER 3: INTELLIGENCE                                              │
│  Specialized Subagents (Knowledge, Coding, Review)                 │
│  Each with scoped tools, model selection, and role boundaries      │
├─────────────────────────────────────────────────────────────────────┤
│  LAYER 4: DATA & KNOWLEDGE                                         │
│  SQLite Index (structured) + Pinecone Vector DB (semantic)         │
│  Fidelity Gates at every pipeline boundary                         │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Technology Decision: Claude Code with Built-in Subagents

During the research phase, we evaluated four implementation approaches:

| Approach | Verdict | Rationale |
|----------|---------|-----------|
| External frameworks (LangGraph, CrewAI, AutoGen) | **Rejected** | Additional dependency your team doesn't use; abstraction overhead doesn't map to this use case |
| Raw Anthropic API | **Rejected** | Would require reimplementing file editing, terminal access, Git operations, and MCP support — weeks of redundant engineering |
| Claude Agent SDK (Python classes) | **Superseded** | Functional but adds a Python SDK dependency when Claude Code CLI already has native subagent orchestration built-in |
| **Claude Code CLI with Built-in Subagents** | **Selected** | Since Opus 4.6 (Feb 5, 2026), Claude Code has native subagent orchestration via `.claude/agents/*.md` Markdown files. Agents are defined declaratively — model selection, tool restrictions, MCP routing, and permission modes are all configuration, not code. FastAPI only handles webhook reception and dashboard. |

**Why this matters:** Claude Code's built-in subagent system gives us the full orchestration layer — agent spawning, model selection per agent, tool restrictions, MCP server routing, context isolation, and session management — without writing orchestration code. Agents are defined as Markdown files with YAML frontmatter, not Python classes.

**Reference implementations that validate this approach:**
- [anthropics/claude-code-action](https://github.com/anthropics/claude-code-action) — Official Anthropic GitHub Action using Claude Code subagents (5,592 stars)
- [disler/claude-code-hooks-multi-agent-observability](https://github.com/disler/claude-code-hooks-multi-agent-observability) — Multi-agent monitoring with built-in orchestration (1,038 stars)
- [claude-did-this/claude-hub](https://claude-did-this.com/claude-hub/getting-started/complete-workflow) — Production GitHub webhook workflow
- [Anthropic Docs: Custom Subagents](https://docs.anthropic.com/docs/en/sub-agents) — Official documentation for `.claude/agents/` definitions

### 3.3 Agent Architecture: Manager Pattern with Subagents

Based on analysis of the [Atomic.Net orchestration pattern](https://github.com/SteffenBlake/Atomic.Net) and Claude Code's built-in agent capabilities, we recommend the **Manager Pattern** (as defined in OpenAI's Practical Guide to Building Agents):

> *"The manager pattern empowers a central LLM — the 'manager' — to orchestrate a network of specialized agents seamlessly through tool calls. Instead of losing context or control, the manager intelligently delegates tasks to the right agent at the right time."*
> — OpenAI, A Practical Guide to Building Agents (2025)

**Why subagents, not agent teams:**

| Criterion | Subagents | Agent Teams | Our Decision |
|-----------|-----------|-------------|--------------|
| Communication | Results return to orchestrator | Peers message each other directly | Our pipeline is sequential, not collaborative → **Subagents** |
| Token cost | Lower (results are summarized) | Higher (each teammate = separate Claude instance) | Budget-sensitive non-profit → **Subagents** |
| Coordination | Orchestrator manages all routing | Shared task list, self-organizing | We need controlled pipeline routing → **Subagents** |
| Complexity | Simpler to implement and debug | Requires team config, inboxes, shutdown protocols | MVP timeline → **Subagents** |

**Upgrade path:** If future requirements demand peer-to-peer agent collaboration (e.g., knowledge agent and coding agent need to discuss trade-offs), the architecture supports migration to Agent Teams without rewriting the pipeline.

### 3.4 Agent Definitions

Agents are defined as Markdown files in `.claude/agents/` with YAML frontmatter. Claude Code reads these at session start and automatically delegates based on the `description` field.

**Knowledge Agent** (`.claude/agents/knowledge-agent.md`):
```yaml
---
name: knowledge-agent
description: Queries Pinecone for C++/Clang review knowledge. Use proactively.
model: haiku
tools: Read, Grep, Glob
mcpServers:
  - pinecone-search
permissionMode: plan
---
You are a C++ knowledge retrieval specialist for LLVM/Clang.
Query the Pinecone MCP for relevant code review patterns and history.
Return a structured context summary. DO NOT write or modify any code.
```

**Coding Agent** (`.claude/agents/coding-agent.md`):
```yaml
---
name: coding-agent
description: Implements code changes and fixes for C++ projects
model: opus
permissionMode: bypassPermissions
---
You are a senior C++ developer working on LLVM/Clang.
Implement changes based on the knowledge context provided.
Follow LLVM coding standards. Create clean, minimal diffs.
```

**Review Agent** (`.claude/agents/review-agent.md`):
```yaml
---
name: review-agent
description: Reviews code changes for C++ quality and best practices
model: sonnet
tools: Read, Grep, Glob, Bash
disallowedTools: Write, Edit
permissionMode: plan
---
You are a code review specialist for LLVM/Clang.
Review changes made by the coding agent. Check correctness,
style compliance, and alignment with historical review patterns.
Output EXACTLY: "ALL CLEAR" + summary, or "NEEDS FIXES" + issues.
```

**Orchestrator** (`.claude/agents/orchestrator.md`):
```yaml
---
name: orchestrator
description: Orchestrates C++ code review pipeline
model: sonnet
tools: Task(knowledge-agent, coding-agent, review-agent), Read, Grep, Glob
permissionMode: bypassPermissions
---
You are the orchestrator. NEVER write code. ONLY delegate.
Pipeline: knowledge-agent → coding-agent → review-agent.
Max 3 review loops. Report results with cost tracking.
```

**Key advantage:** No Python orchestration code needed. Claude Code handles subagent spawning, model selection, tool restrictions, MCP routing, and context isolation natively.

### 3.5 Pipeline Workflow

```
GitHub Event (webhook)
    │
    ▼
┌──────────────────────────┐
│  ORCHESTRATOR (FastAPI)   │  ← Receives event, validates signature
│  Routes to pipeline:      │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│  1. KNOWLEDGE AGENT      │  ← Queries Pinecone + SQLite
│     Model: Sonnet         │  ← Returns: structured context
│     Tools: Read-only      │  ← Cost: LOW (~$0.01-0.05 per query)
└──────────┬───────────────┘
           │ context
           ▼
┌──────────────────────────┐
│  2. CODING AGENT          │  ← Receives context + task
│     Model: Opus           │  ← Implements fix, creates diff
│     Tools: Full access    │  ← Cost: HIGH (~$0.50-2.00 per task)
└──────────┬───────────────┘
           │ code changes
           ▼
┌──────────────────────────┐
│  3. REVIEW AGENT          │  ← Reviews changes
│     Model: Sonnet         │  ← Runs tests, checks quality
│     Tools: Read + Bash    │  ← Cost: MEDIUM (~$0.10-0.30)
└──────────┬───────────────┘
           │
       ┌───┴───┐
       │       │
    ALL CLEAR  FEEDBACK
       │       │
       ▼       └──→ Back to CODING AGENT (loop)
  Create PR            (max 3 iterations)
  on GitHub
```

**Critical design principle** (adapted from the Atomic.Net Manager Pattern):

> The orchestrator NEVER writes code. It ONLY delegates to the three specialized agents and manages the review loop. This separation prevents context pollution and ensures each agent operates within its defined role.

---

## 4. Data Integrity: Fidelity Gates

Adapted from the Manifest-Receipt Reconciliation pattern observed in TheAuditor v2 (a proven database-first static analysis tool with verified accuracy on 834,000+ code elements):

### 4.1 The Problem

When scraping 100,000+ PR comments from LLVM/Clang and loading them into a knowledge base, any silent data loss directly degrades agent quality. Without verification, we cannot guarantee that the knowledge base is complete.

### 4.2 The Solution: Manifest-Receipt at Every Pipeline Boundary

```
STEP 1: SCRAPE                 STEP 2: INDEX                 STEP 3: EMBED
─────────────────              ─────────────────             ─────────────────
Manifest:                      Manifest:                     Manifest:
"Scraping 7,342 PRs            "Indexing 45,891              "Generating 45,891
 with 45,891 comments"          comments into SQLite"          embeddings"

Receipt:                       Receipt:                      Receipt:
"Scraped 7,342 PRs,            "Indexed 45,891 comments,     "Generated 45,891
 extracted 45,891 comments,     0 duplicates, 0 failures"     embeddings, all
 0 API errors"                                                dimensions valid"

Reconciliation:                Reconciliation:               Reconciliation:
✅ 45,891 == 45,891            ✅ 45,891 == 45,891           ✅ 45,891 == 45,891
   Delta: 0                       Delta: 0                      Delta: 0
   GATE PASSED                    GATE PASSED                   GATE PASSED
```

**Deliverable:** A Python module (`fidelity.py`) implementing this verification system, producing auditable reports at every pipeline stage.

---

## 5. Database-First Knowledge Layer

### 5.1 Dual-Database Architecture

Instead of relying solely on vector search (which can hallucinate or return irrelevant results), we propose a **hybrid approach**:

| Database | Purpose | Query Type | Example |
|----------|---------|------------|---------|
| **SQLite** (structured) | Exact lookups, statistics, relationships | Deterministic | "How many times has Richard Smith reviewed template-related PRs?" → `SELECT COUNT(*) ...` |
| **Pinecone** (semantic) | Similarity search, pattern matching | Probabilistic | "Find review comments similar to this code change" → vector cosine similarity |

### 5.2 Why Both?

The SQLite index serves as **ground truth** for the LLM agents. When the knowledge agent queries "What are the common review patterns for template metaprogramming?", it gets:

1. **From SQLite:** Exact counts, specific reviewers, concrete PR numbers — facts the LLM cannot hallucinate
2. **From Pinecone:** Semantically similar review comments — context the LLM uses for nuanced understanding

This dual approach was validated by TheAuditor's architecture, where deterministic database queries eliminated LLM hallucination for factual code analysis (verified accuracy: ~100% on syntactic queries, 89–100% on semantic queries across 834,000 code elements).

---

## 6. Infrastructure & Cost Model

### 6.1 Deployment Architecture

```
Azure VM (B2ms, Ubuntu 22.04)
├── FastAPI Server (uvicorn, systemd service)     ← 24/7, handles webhooks
├── SQLite Database                                ← Knowledge index, agent logs
├── MCP Server (Pinecone, npm package)            ← 24/7, vector DB access
├── nginx (reverse proxy, HTTPS via Let's Encrypt) ← 24/7, routing
└── Claude Code CLI (built-in subagents)            ← On-demand, API calls only
```

### 6.2 Monthly Cost Breakdown

| Component | Runtime | Monthly Cost | Paid By |
|-----------|---------|-------------|---------|
| Azure VM (B2ms) | 24/7 | ~$60 | $5,000 MS credits |
| Azure Blob Storage | Persistent | ~$5 | MS credits |
| Azure Key Vault | 24/7 | ~$1 | MS credits |
| Claude API (Sonnet) | On-demand | ~$50–200 | Anthropic API key |
| Claude API (Opus) | On-demand | ~$100–500 | Anthropic API key |
| **Total infrastructure** | | **~$66/month** | **Credits: 76+ months** |
| **Total with API usage** | | **~$216–766/month** | **Depends on volume** |

### 6.3 Cost Optimization Strategy

| Agent | Model | Frequency | Cost per Invocation | Rationale |
|-------|-------|-----------|--------------------|-----------| 
| Knowledge | Haiku 4.5 | Every event | ~$0.01–0.05 | Simple retrieval, cheapest |
| Coding | Opus 4.6 | Only when code changes needed | ~$0.50–2.00 | Quality critical for C++ |
| Review | Sonnet 4.5 | After every code change | ~$0.10–0.30 | Good quality, moderate cost |

**Key insight:** The knowledge agent runs most frequently but is the cheapest. The expensive coding agent only runs when actual code changes are required. This natural cost gradient keeps the system economical.

---

## 7. Risk Assessment & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| MCP Server access delayed | Medium | High | Fallback: local FAISS vector DB with sample data for demo |
| Claude API rate limits | Low | Medium | Queue system with exponential backoff; session resume for long tasks |
| Agent quality on C++ code | Medium | High | Review agent loop with max 3 iterations; human escalation on failure |
| Azure VM downtime | Low | Medium | systemd auto-restart; health check endpoint |
| Data pipeline integrity | Medium | High | Fidelity Gates with manifest-receipt verification |
| Token cost overrun | Medium | Medium | `maxTurns` parameter per agent; 3-tier model selection (Haiku/Sonnet/Opus); cost tracking dashboard |

---

## 8. Deliverables & Timeline

### Phase 1: MVP & Proof of Concept (Feb 10–16, 2026)

| # | Deliverable | Format | Owner |
|---|-------------|--------|-------|
| 1 | Architecture documentation (this document) | MD | SG |
| 2 | CLI comparison (Cursor vs Claude Code, 9 dimensions) | MD | SG ✅ |
| 3 | Hook systems analysis (Cursor 8 vs Claude Code 15 events) | MD | SG ✅ |
| 4 | Agent architecture evaluation (Swarm vs Subagents vs Teams) | MD | SG ✅ |
| 5 | **Functioning webhook server on Azure** | Python/FastAPI | SG |
| 6 | **Multi-agent pipeline (Knowledge → Coding → Review)** | Python | SG |
| 7 | **Live monitoring dashboard** | HTMX/WebSocket | SG |
| 8 | **End-to-end demo** (GitHub issue → agent response) | Live | SG |
| 9 | Cost projection model | Spreadsheet | SG |

### Phase 2: Production Integration (Feb–Apr 2026)

| # | Deliverable | Owner |
|---|-------------|-------|
| 1 | MVP → production migration guide | SG + Will's team |
| 2 | MCP server integration with live Pinecone data | Will's team |
| 3 | Self-hosted runner setup with build caches | Will's team |
| 4 | Security hardening (API keys, secrets, access control) | Will's team |
| 5 | Agent Teams upgrade (if subagent limitations emerge) | SG |

### Phase 3: Ongoing Operations (Apr–Sep 2026)

| # | Deliverable | Owner |
|---|-------------|-------|
| 1 | Monthly agent performance reviews | SG |
| 2 | Model upgrades as new Claude versions release | SG |
| 3 | New agent types (CI-fixer, documentation agent) | SG |
| 4 | Monitoring and alerting via Azure Monitor | Will's team |

---

## 9. Success Criteria

The MVP will be evaluated against these measurable criteria during the mid-February meeting:

| # | Criterion | Target | Measurement |
|---|-----------|--------|-------------|
| 1 | Webhook response time | < 10 seconds | Time from GitHub event to first agent action |
| 2 | Multi-agent pipeline | 3 agents working in sequence | Dashboard shows Knowledge → Coding → Review |
| 3 | MCP integration | Successful Pinecone query | Agent returns relevant C++ context |
| 4 | Session persistence | State survives across events | Agent resumes conversation with `--resume` |
| 5 | End-to-end loop | GitHub → Agent → GitHub | Issue created → agent comment posted automatically |
| 6 | Observability | Full visibility | Dashboard shows live logs, steps, and costs |
| 7 | Data integrity | 100% verified | Fidelity Gates show zero data loss in pipeline |

---

## 10. References & Prior Art

| Source | Relevance | URL |
|--------|-----------|-----|
| OpenAI, "A Practical Guide to Building Agents" | Manager Pattern, guardrails, tool design | [cdn.openai.com](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf) |
| Anthropic, Claude Code Built-in Subagents | Custom agent definitions via `.claude/agents/` | [docs.anthropic.com](https://docs.anthropic.com/docs/en/sub-agents) |
| Anthropic, Claude Code Agent Teams | Multi-agent team orchestration (experimental) | [code.claude.com](https://code.claude.com/docs/en/agent-teams) |
| Anthropic, Claude Code Headless Mode | CLI programmatic usage | [code.claude.com](https://code.claude.com/docs/en/headless) |
| Atomic.Net, Manager Agent Pattern | Pure orchestrator that never codes | [github.com/SteffenBlake](https://github.com/SteffenBlake/Atomic.Net) |
| TheAuditor v2 (AGPL-3.0) | Database-First architecture, Fidelity Gates | [github.com/TheAuditorTool](https://github.com/TheAuditorTool/Auditor) |
| e2b-dev/claude-code-fastapi | FastAPI + Claude Code reference template | [github.com/e2b-dev](https://github.com/e2b-dev/claude-code-fastapi) |
| anthropics/claude-code-action | Official Anthropic GitHub Action with /dedupe bot (5,592 stars) | [github.com/anthropics](https://github.com/anthropics/claude-code-action) |
| claude-did-this/claude-hub | Production GitHub webhook workflow | [claude-did-this.com](https://claude-did-this.com/claude-hub/getting-started/complete-workflow) |
| Carlini (Anthropic), 16-Agent C Compiler | Agent Teams at scale, practical limits | [arstechnica.com](https://arstechnica.com/ai/2026/02/sixteen-claude-ai-agents-working-together-created-a-new-c-compiler) |
| Swarm Orchestration Skill (290 stars) | TeammateTool & Task system patterns | [gist.github.com/kieranklaassen](https://gist.github.com/kieranklaassen/4f2aba89594a4aea4ad64d753984b2ea) |

---

## Appendix A: Glossary

| Term | Definition |
|------|-----------|
| **Built-in Subagents** | Claude Code's native system for spawning specialized agents via `.claude/agents/` Markdown files |
| **Subagent** | A specialized agent spawned by a parent agent, with its own context window and tool restrictions |
| **Agent Team** | Claude Code's multi-agent system where teammates communicate directly (peer-to-peer) |
| **MCP** | Model Context Protocol — standard for connecting LLMs to external data sources and tools |
| **Fidelity Gate** | A verification checkpoint that compares expected data (manifest) with actual data (receipt) |
| **Manager Pattern** | Orchestration approach where a central agent delegates to specialists without doing work itself |

---

## Appendix B: Research Artifacts

The following research documents were produced during the evaluation phase and are available for reference:

1. `RESEARCH-CLI-HOOKS-ARCHITECTURE-DE.md` — Cursor CLI vs Claude Code CLI comparison (German)
2. `RESEARCH-CLI-HOOKS-ARCHITECTURE-EN.md` — Same document in English
3. `PROPOSAL-FIDELITY-ARCHITECTURE-THEAUDITOR.md` — Database-First architecture analysis
4. `QA-ARCHITECTURE-DECISIONS.md` — 6 key architecture questions answered with sources
5. `PROJECT-PLAN.md` — Full project plan with timeline, scope, and business strategy

---

---

## Appendix C: FastAPI Workflow — Was macht der Server eigentlich?

*Dieses Appendix erklärt die Architektur für Teammitglieder, die nicht täglich mit Python/Backend arbeiten. Kompatibel mit dem C++-Team, da Python als Orchestrierungssprache fungiert — der eigentliche C++-Code wird weiterhin von den Agents geschrieben.*

### Was ist FastAPI?

- **Sprache:** Python (nicht JavaScript)
- **Zweck:** Das Backend (die Server-Seite) bauen
- **Der Name:** "FastAPI" — extrem schnell sowohl in der Code-Ausführung als auch in der Entwicklungsgeschwindigkeit

### FastAPI im Architektur-Diagramm

```
┌─────────────────────────────────────────────────────────────────────┐
│  OBEN: Frontend / Dashboard                                         │
│  Was der Benutzer sieht                                             │
│  Geschrieben in: HTMX (oder React/Next.js)                         │
│  → Die "schöne Hülle"                                              │
├─────────────────────────────────────────────────────────────────────┤
│  UNTEN: Backend / Server                                            │
│  Hier passiert die eigentliche Arbeit und Logik                     │
│  Geschrieben in: Python mit FastAPI                                 │
│  → Das "Gehirn"                                                    │
└─────────────────────────────────────────────────────────────────────┘
```

**Die Aufgabe von FastAPI in diesem System:**

1. Es fungiert als **"Orchestration Server"** (der Dirigent des Orchesters)
2. Es nimmt Befehle vom Dashboard entgegen (über WebSocket)
3. Es empfängt Nachrichten von außen (**Webhooks** — dazu gleich mehr)
4. Es entscheidet, **welcher KI-Agent** gestartet werden muss

### Verbindung zu Webhooks

Im Architektur-Diagramm sieht man den "Webhook Router". Das ist die Brücke zwischen GitHub und unseren Agents:

| Konzept | Wo es läuft | Was es tut |
|---------|-------------|-----------|
| **Cursor Hooks** | Lokal auf deinem PC, während du codest | IDE-Events abfangen (z.B. nach File-Save) |
| **GitHub Webhooks** | Über das Internet, von GitHub zu unserem Server | Repo-Events abfangen (z.B. neuer PR) |

**Konkretes Szenario:**

```
1. Jemand macht auf GitHub einen Pull Request (Code-Änderungsvorschlag)
       │
       ▼
2. GitHub feuert einen Webhook (ein HTTP-Signal) ab
       │
       ▼
3. Dieser Webhook landet bei unserem FastAPI Server
       │
       ▼
4. Der "Webhook Router" in FastAPI sieht:
   "Aha, ein Pull Request! Ich muss den Review Agent losschicken."
       │
       ▼
5. FastAPI startet den Review Agent (Claude Code Built-in Subagent)
       │
       ▼
6. Agent reviewed den Code, schreibt Kommentar auf GitHub
```

### Zusammenfassung für die Erklärung an Kollegen

> *"FastAPI ist das Python-Framework, das wir für unseren Server benutzen. Im Diagramm ist das der untere Kasten. Während das Frontend (oben) JavaScript sein kann, nutzen wir für die schwere Logik im Hintergrund Python mit FastAPI. Es ist dafür zuständig, die Signale (Webhooks) von außen entgegenzunehmen und die richtigen KI-Agenten zu steuern. Es ist quasi die Einsatzzentrale, die die Befehle verteilt."*

### Warum Python/FastAPI für ein C++-Team?

| Bedenken | Antwort |
|----------|---------|
| "Wir sind ein C++-Team, warum Python?" | Python orchestriert nur — der eigentliche C++-Code wird weiterhin von den Agents in C++ geschrieben |
| "Ist Python schnell genug?" | FastAPI ist async, handled tausende Webhooks/Sekunde. Die "schwere Arbeit" macht Claude, nicht Python |
| "Noch ein Stack zu maintainen?" | FastAPI ist ~200 Zeilen Code für unseren Use Case. Minimal, kein Framework-Bloat |
| "Kann unser Team das lesen?" | Python ist die lesbarste Programmiersprache. C++-Devs können es in 30 min lesen |

---

## Appendix D: Methodology — Wie dieses Dokument erstellt wurde

*Dieser Abschnitt dokumentiert den Research- und Erstellungsprozess, damit er reproduzierbar ist und als Template für zukünftige Consulting-Dokumente dienen kann.*

### Phase 1: Research-Methodik

**Frage:** Wie schreiben Senior Consultants bei Top-Firmen (McKinsey, BCG, Bain, Deloitte) technische Architektur-Proposals?

**Recherchierte Frameworks:**

| Framework | Quelle | Key Insight |
|-----------|--------|-------------|
| **Pyramid Principle** | Barbara Minto (McKinsey) | Lead with the answer first. Nicht erst Background aufbauen, sondern sofort die Recommendation. Dann Argumente, dann Evidenz. |
| **SCR Framework** | McKinsey Standard | **S**ituation (was ist heute der Fall) → **C**omplication (was ist das Problem) → **R**esolution (was ist die Lösung). Zwingt zu klarer Problemdefinition vor der Lösung. |
| **4-Layer Reference Architecture** | OpenAI "Practical Guide to Building Agents" (32 Seiten, komplett gelesen) | Experience → Orchestration → Intelligence → Data. Jede Schicht hat klare Verantwortung. Manager Pattern vs Decentralized Pattern. Guardrails als First-Class-Konzept. |
| **Agentic Enterprise** | Deloitte (2026), Salesforce Architects | Composable Design, Governance Focus, Elastic Workforce Capacity. Business-Sprache für technische Konzepte. |
| **Consulting Proposal Template** | Ex-McKinsey/BCG (SlideWorks) | Executive Summary, Problem Statement, Technical Approach, Management Plan, Team, Timeline, Cost, ROI. Systematische Proposals → 55% höhere Win Rate. |

**Zusätzliche technische Research:**

| Quelle | Was gelernt |
|--------|-------------|
| OpenAI Agent Guide (PDF, 32 Seiten) | Agent = Model + Tools + Instructions. Manager Pattern Code-Beispiele. Guardrails mit Input/Output-Validierung. Wann Single- vs Multi-Agent. |
| Atomic.Net `manager.agent.md` | Pure Orchestrator Prinzip: "YOUR ONLY JOB IS TO DELEGATE." Verbotsliste für den Manager. 5 spezialisierte Agents. |
| TheAuditor v2 (AGPL-3.0) | Database-First Pattern: SQLite als Ground Truth. Manifest-Receipt für Datenintegrität. In-Language Extraction (libclang für C++). Verified auf 834k+ Code-Elementen. |
| Discord-Diskussion (Claude Code Community) | Agent Teams vs Subagents Kostendifferenz. Session Persistence Limitationen. Graphiti-Evaluation (verworfen — löst nicht die echten Pain Points). |
| claude-hub / e2b-dev Templates | Production-ready FastAPI + Claude Code Patterns. Docker-Isolation. Webhook-Signatur-Validierung. |

### Phase 2: Synthese-Methodik

**Ansatz:** Nicht einfach Research zusammenfassen, sondern Frameworks *kombinieren*:

1. **Struktur** vom McKinsey Pyramid Principle (Recommendation → Evidence)
2. **Narrative** vom SCR Framework (Situation → Complication → Resolution)
3. **Technische Tiefe** vom OpenAI Agent Guide (4-Layer, Manager Pattern, Guardrails)
4. **Datenintegrität** von TheAuditor (Database-First, Fidelity Gates)
5. **Orchestration** von Atomic.Net (Pure Delegation, Role Boundaries)
6. **Business-Sprache** von Deloitte/Salesforce (Composable, Governance, Elastic)

### Phase 3: Dokument-Erstellung

**Werkzeuge:**
- Cursor IDE (Agent Mode) mit claude-4.6-opus-high-thinking
- Web-Recherche via integrierte Suchtools (kein Perplexity MCP)
- WebFetch für PDFs und GitHub-Repos
- Kein externer API-Zugriff außer öffentlichen Webseiten

**Schreib-Reihenfolge:**
1. Executive Summary (Recommendation first — Pyramid Principle)
2. Situation (was funktioniert heute)
3. Complication (die 5 Bottlenecks, als Tabelle quantifiziert)
4. Resolution (4-Layer Architektur mit Code-Beispielen)
5. Kosten-Modell (transparent, mit Azure Credits)
6. Risk Assessment (6 Risiken, jedes mit Mitigation)
7. Success Criteria (7 messbare Kriterien für die Demo)
8. Appendices (Glossar, Artifacts, Workflow, Methodology)

### Template für zukünftige Consulting-Dokumente

```markdown
# [Title]: [Specific Technical Recommendation]

**Prepared for:** [Client]
**Prepared by:** [Consultant]
**Date:** [Date]
**Version:** [Version]

## Executive Summary
→ Pyramid Principle: Recommendation FIRST
→ Outcomes-Tabelle: Current State vs Proposed State
→ One-line cost summary

## 1. Situation
→ What works today (be generous, acknowledge existing work)

## 2. Complication
→ What's broken (quantified, not vague)
→ Business impact (time wasted, money lost)

## 3. Resolution
→ Architecture overview (4-layer diagram)
→ Technology decision (comparison table with Verdict column)
→ Implementation details (code examples if technical audience)

## 4. [Domain-Specific Section]
→ e.g., Data Integrity, Security, Performance

## 5. Cost Model
→ Monthly breakdown, who pays what
→ Optimization strategy

## 6. Risk Assessment
→ Table: Risk | Likelihood | Impact | Mitigation

## 7. Timeline & Deliverables
→ Phase 1 (MVP), Phase 2 (Production), Phase 3 (Ongoing)

## 8. Success Criteria
→ Measurable, specific, tied to demo/meeting

## References
→ Real sources, not hallucinated

## Appendices
→ Glossary, Methodology, Team Explanations
```

### Recherche-Zeitaufwand

| Phase | Dauer | Aktivität |
|-------|-------|-----------|
| Research: Consulting Frameworks | ~15 min | Web-Suche: McKinsey Pyramid, SCR, Proposal Templates |
| Research: OpenAI Agent Guide | ~10 min | PDF komplett gelesen (32 Seiten), Key Patterns extrahiert |
| Research: Deloitte/Salesforce | ~5 min | Agentic Enterprise Reference Architecture |
| Synthese: Frameworks kombinieren | ~10 min | 6 Quellen zu einer kohärenten Struktur zusammenführen |
| Schreiben: Consultant Paper | ~20 min | 414 Zeilen, 10 Sections + 4 Appendices |
| Update: PROJECT-PLAN.md | ~10 min | Tech-Entscheidung, Deliverables, Change Log |
| **Total** | **~70 min** | **Vom leeren File zum fertigen Consulting-Dokument** |

---

*This document follows the Pyramid Principle (Minto/McKinsey): recommendation first, supporting evidence second. Structure adapted from industry-standard consulting deliverable formats (Situation → Complication → Resolution) combined with technical architecture best practices (OpenAI Agent Guide 4-layer model, Deloitte Agentic Enterprise framework).*

*Prepared: February 10, 2026*  
*Next review: Mid-February 2026 meeting with Will Pak*
