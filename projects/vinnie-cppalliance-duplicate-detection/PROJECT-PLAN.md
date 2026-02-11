# C++ Alliance - LLVM/Clang Knowledge Mining & Code Review Agent

## Project Overview

**Client:** Vinnie Falco (@vinniefalco)  
**Organization:** [C++ Alliance](https://github.com/cppalliance)  
**Technical Contact:** Will Pak  
**Start Date:** February 2026  
**Status:** 🟢 ACTIVE - Awaiting sync with Will Pak

---

## 🚨 PROJECT EVOLUTION

| Phase | Original Understanding | Actual Scope |
|-------|----------------------|--------------|
| Initial | Duplicate detection for 7k issues | ❌ Not the main goal |
| Expanded | Knowledge extraction from PR comments | ✅ Part of it |
| **Final** | **Build an AI agent that reviews PRs like Richard Smith** | ✅ THE GOAL |

**Key Quote from Vinnie:**
> "the goal is to create an agent which can review pull requests using the same mental model and experience that Richard Smith uses when he reviews pull requests"

---

## Background & Context

### How This Started

Vinnie reached out with an agenda for a huddle containing two projects:

```
Agenda for huddle:
1. wg21 project
   a. knowledge capture workflow
   b. GitHub driven
   c. prompt engineering
   d. semantic comparison
2. clang project
   a. scraping issue/PR comments
   b. prompt engineering
```

His core problem statement:
> "We have the clang repo with 7,000 open issues and I want a robust way to detect duplicates. I was thinking we can transform each issue into an embedding and then maybe do a matrix comparison to generate a 'similarity signal?'"
>
> "A general algorithm to detect duplicate open issues on GitHub would have a lot of value"

### Client Profile

- **Vinnie Falco** is a known C++ contributor and part of the C++ Alliance
- Works with Clang/LLVM-based tools (e.g., `mrdocs` - documentation generator)
- Technical background - understands embeddings, matrix comparison
- Pragmatic: wants "most effective and cheapest" solution
- Not the owner of LLVM - contributor/maintainer helping the community

### The Repository

- **Repo:** `llvm/llvm-project` (public)
- **Target:** Issues labeled `clang`
- **Scale:** ~7,000 open issues
- **Access:** Public - no special permissions needed

---

## Project Scope

### 🔄 SCOPE UPDATE (Feb 4, 2026)

**Original Ask:** Duplicate detection for 7k Clang issues
**Actual Ask:** Knowledge mining from the entire PR/Issue conversation history

Vinnie clarified:
> "what we want are the comments, and for pull requests as well"
> "the pull request comments are tied to specific commits, files, and lines"
> "what we want to do is reconstruct the entire history of the human interactions, to capture the knowledge implicit in the code reviews"
> "when Richard Smith reviews a pull request, he leaves comments. there is a back and forth with the contributor. we want to capture and analyze that"

**This is NOT just duplicate detection. This is KNOWLEDGE EXTRACTION from code reviews.**

---

### ✅ Phase 1: Data Acquisition (ACTIVE)

**Objective:** Scrape and structure the complete conversation history from LLVM/Clang.

#### Data Sources

| Source | Content | API Endpoint |
|--------|---------|--------------|
| Issues | Title, body, labels | `GET /repos/{owner}/{repo}/issues` |
| Issue Comments | Full conversation threads | `GET /repos/{owner}/{repo}/issues/{issue_number}/comments` |
| Pull Requests | Title, body, diff | `GET /repos/{owner}/{repo}/pulls` |
| PR Review Comments | Line-level feedback (tied to commits/files) | `GET /repos/{owner}/{repo}/pulls/{pull_number}/comments` |
| PR Reviews | Approval/request changes | `GET /repos/{owner}/{repo}/pulls/{pull_number}/reviews` |

#### Challenges

- **Rate Limits:** 5,000 requests/hour with PAT
- **Scale:** 7k+ issues + PRs + all comments = potentially 100k+ API calls
- **Structure:** PR comments are tied to specific commits, files, lines

#### Strategy

1. Start with a small subset (100 PRs with comments)
2. Build the data pipeline
3. Validate structure
4. Scale incrementally

### ✅ Phase 2: Knowledge Extraction

**Objective:** Extract implicit knowledge from code review conversations.

#### Potential Outputs

1. **Expertise Mapping** - "Richard Smith is the expert on X topic"
2. **Common Patterns** - "These types of bugs always get this feedback"
3. **Knowledge Base** - Searchable repository of review insights
4. **Training Data** - For fine-tuning models on C++ best practices

### ⏸️ Phase 3: Duplicate Detection (DEPRIORITIZED)

**Original objective** - now secondary to knowledge extraction.
Same approach: embeddings + similarity matrix, but applied to extracted knowledge.

---

## 🎯 THE REAL PROJECT: LLVM/Clang Code Review Agent

### Vision

Build an AI agent that can review C++ pull requests using the **collective expertise** extracted from the entire LLVM/Clang review history.

**Richard Smith was mentioned as an EXAMPLE** of the kind of expert reviewer whose knowledge should be captured – not the only source.

### What This Requires

| Component | Description | Complexity |
|-----------|-------------|------------|
| **Data Pipeline** | Scrape ALL PR reviews, comments, and feedback from LLVM/Clang | High |
| **Knowledge Extraction** | Identify patterns, best practices, common feedback across ALL reviewers | High |
| **Agent Architecture** | RAG or fine-tuned model for code review | Very High |
| **Integration** | GitHub bot that auto-reviews PRs | Medium |

### Key Insight

The goal is to capture the **implicit knowledge** from code review conversations:
- What patterns do experienced reviewers flag?
- What feedback is commonly given?
- What are the unwritten rules of LLVM/Clang code quality?

Richard Smith is just one (prominent) example of the expertise they want to extract.

### Technical Approaches

| Approach | Pros | Cons |
|----------|------|------|
| **RAG** | No training needed, uses existing reviews as context | May lack nuance |
| **Fine-tuning** | Captures style and patterns deeply | Needs lots of data, expensive |
| **Hybrid** | Best of both worlds | Most complex |

---

## Contacts

| Person | Role | Status |
|--------|------|--------|
| **Vinnie Falco** | Project Owner, C++ Alliance | ✅ Connected |
| **Will Pak** | Technical Lead (?) | 🟡 Awaiting response |
| **Richard Smith** | Subject Matter Expert | ❓ Unknown involvement |

---

## Meeting Notes: Will Pak Sync (Feb 4, 2026)

### Current Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     C++ ALLIANCE AI INFRASTRUCTURE                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────────┐   │
│  │ GitHub Repo  │────▶│ Claude Agent │────▶│ MCP Server       │   │
│  │ (Cappy, etc) │     │ (on GitHub)  │     │ (Vector DB)      │   │
│  └──────────────┘     └──────────────┘     └──────────────────┘   │
│         │                    │                      │              │
│         │                    ▼                      │              │
│         │            ┌──────────────┐               │              │
│         │            │ GitHub       │               │              │
│         └───────────▶│ Runners      │◀──────────────┘              │
│                      │ (CI/CD)      │                              │
│                      └──────────────┘                              │
│                             │                                      │
│                             ▼                                      │
│                      ┌──────────────┐                              │
│                      │ JSON → MD →  │                              │
│                      │ Vector DB    │                              │
│                      └──────────────┘                              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### What They Already Have (PoC)

| Component | Status | Notes |
|-----------|--------|-------|
| Claude Agent on GitHub | ✅ Working | Can pull data, request commits, suggest fixes |
| MCP Package | ✅ Published | Connected to Claude Code |
| Vector Database | ✅ Exists | C++ & Boost high-quality data |
| Data Pipeline | 🟡 Partial | JSON format, needs MD conversion |
| GitHub Runners | ⚠️ Slow | Up to 2 hours delay, sometimes full day |

### Current Problems

1. **Speed:** GitHub Runner allocation takes too long (minutes to hours)
2. **Feedback Loop:** Users don't know when AI is working
3. **Compatibility:** Claude Code sometimes incompatible with Runner
4. **Cost:** Runner costs for every interaction
5. **Iteration:** Very slow development cycle

### What They Need

1. **Webhooks** for real-time feedback
2. **Agent Orchestration** - multiple agents working together
3. **Faster infrastructure**
4. **Constant Vector DB updates** (daily scraping)

### Foundation Model

- **Sonnet or Opus 4.5**
- Cost optimization needed (Opus is expensive)
- Accumulating: docs, issues, books, comments → MCP Server

---

## MY SCOPE

### Arbeitsteilung: Wer macht was?

| Verantwortung | Wer | Details |
|---------------|-----|---------|
| **Orchestration Layer Design** | **SG (ich)** | Multi-Agent Architektur, Agent-Rollen, Kommunikation |
| **Funktionierender MVP / PoC** | **SG (ich)** | Webhook-Server + Agents auf Azure, LIVE demonstrierbar |
| **CLI-Evaluation** | **SG (ich)** | Cursor CLI vs Claude Code CLI Vergleich |
| **Token-Kosten-Strategie** | **SG (ich)** | Welches LLM für welchen Agent (Opus vs Sonnet vs GPT-4o) |
| **Infrastruktur (Production)** | **Will's Team** | Runner-Optimierung, CI-Pipelines, Security Hardening |
| **MCP Server (Pinecone)** | **Will's Team** | ✅ Zugang erhalten (`@will-cppa/pinecone-read-only-mcp`) |
| **Daten-Pipeline** | **Will's Team** | JSON → MD → Pinecone Upload (70-80% fertig) |
| **Production Webhook-Server** | **Will's Team** | Skalierung meines MVP in ihre Infrastruktur |

> **Kernprinzip:** Ich bin der **Architekt + PoC-Builder**. Will's Team ist der **Infrastruktur-Builder**. Mein MVP beweist dass die Architektur funktioniert. Deren Team bringt es in Production.

---

### Phase 1: Research + MVP Build (Now → Mid-February 2026)

| # | Task | Status | Details |
|---|------|--------|---------|
| 1 | Architecture Learning | ✅ Done | CLANG/Boost/Compiler Kontext verstanden |
| 2 | CLI Comparison | ✅ Done | Cursor CLI vs Claude Code - 9 Dimensionen verglichen |
| 3 | Hook-Systeme Research | ✅ Done | Cursor 8 Events vs Claude Code 15 Events |
| 4 | Webhook-Server Architektur | ✅ Done | Design steht (siehe RESEARCH-CLI-HOOKS-ARCHITECTURE-DE.md) |
| 5 | Agent-Architektur Design | ✅ Done | 3 Paradigmen evaluiert: Swarm vs Subagents vs Agent Teams |
| 6 | **Tech-Entscheidung** | ✅ Done | ~~CLI subprocess~~ → **Claude Agent SDK (Python)** — nativ, keine Subprocesses |
| 6b | **Consultant Paper** | ✅ Done | Professionelles Architektur-Dokument (Pyramid Principle, SCR) |
| 6c | **Subagents vs Agent Teams** | ✅ Done | **Subagents** gewählt — sequentielle Pipeline, günstiger, einfacher |
| 6d | **Database-First Pattern** | ✅ Done | SQLite + Pinecone Hybrid mit Fidelity Gates (TheAuditor-Pattern) |
| 7 | **Azure VM aufsetzen** | 🔴 TODO | Ubuntu 22.04, B2ms/D2s_v3 mit $5000 MS Credits |
| 8 | **FastAPI Grundgerüst** | 🔴 TODO | Webhook-Empfang + Signatur + WebSocket + SQLite + Authorized Users Allowlist |
| 9 | **Agent Spawner** | 🔴 TODO | Claude Agent SDK mit `AgentDefinition` + `ClaudeSDKClient` + Repo-Caching |
| 10 | **Agent Dashboard** | 🔴 TODO | HTMX Frontend: Live-Logs, Agent-Status, Steps, Kosten |
| 11 | **MCP Server von Will bekommen** | ✅ Done | `npx -y @will-cppa/pinecone-read-only-mcp` — Zugang erhalten 10. Feb |
| 12 | **Agent-Routing** | 🔴 TODO | Event → Knowledge → Coding → Review Pipeline |
| 13 | **Multi-Agent PoC** | 🔴 TODO | 3 Agents funktionierend mit Dashboard-Logging |
| 14 | **Live Demo vorbereiten** | 🔴 TODO | Test-Repo, Issue erstellen → Agent + Dashboard live |

### Phase 2: Production Integration (Mid-February → September 2026)

| Task | Wer | Details |
|------|-----|---------|
| MVP → Production Migration | Will's Team + SG | Mein PoC in deren Infrastruktur integrieren |
| Self-hosted Runner Setup | Will's Team | Lokale Builds statt GitHub Runner |
| Build-Cache (Boost/Clang) | Will's Team | Vorgebaute Caches für schnellere CI |
| Agent Teams Upgrade | SG | Von Subagents auf Agent Teams wenn nötig |
| Security Hardening | Will's Team | API Keys, Secrets, Zugriffskontrolle |
| Skalierung & Monitoring | Will's Team + SG | Azure Monitor, Logging, Alerting |

---

## TECHNOLOGIE-ENTSCHEIDUNG (UPDATE 10. Feb 2026)

### Warum Claude Agent SDK + FastAPI + Dashboard?

| Option | Urteil | Begründung |
|--------|--------|------------|
| LangGraph/CrewAI/AutoGen | ❌ Verworfen | Extra Dependency, Will's Team kennt es nicht, Abstraktions-Overhead |
| Raw Anthropic API | ❌ Verworfen | File-Edit, Terminal, Git, MCP müsste man SELBST bauen = Wochen |
| Nur Claude Code CLI | 🟡 Halb | Hat alle Tools, aber kein Dashboard/Monitoring |
| ~~FastAPI + Claude Code CLI subprocess~~ | 🟡 Superseded | Funktional, aber subprocess-Management ist fragil |
| **FastAPI + Claude Agent SDK (Python) + Dashboard** | ✅ **ENTSCHIEDEN** | Offizielles Anthropic Python SDK: gleiche Tools wie Claude Code CLI, aber nativ in Python. Keine Subprocesses, typed Messages, built-in Session Management, programmatische Subagent-Definitionen via `AgentDefinition`. |

**Kernlogik:** Das Claude Agent SDK (`pip install claude-agent-sdk`) gibt uns dieselbe Power wie Claude Code CLI (Read, Edit, Bash, Git, MCP) — aber als native Python Library. Agents werden als `AgentDefinition`-Objekte definiert, nicht als CLI-Subprocesses. Sessions werden über `ClaudeSDKClient` verwaltet. MCP-Server werden direkt im Code konfiguriert.

### Warum Subagents, NICHT Agent Teams?

| Kriterium | Subagents | Agent Teams | Unsere Entscheidung |
|-----------|-----------|-------------|---------------------|
| Kommunikation | Zurück an Orchestrator | Direkt untereinander (Peer-to-Peer) | Pipeline ist sequentiell → **Subagents** |
| Token-Kosten | Niedriger (summarized) | HOCH (jeder = eigene Instanz) | Budget-sensitiv (Non-Profit) → **Subagents** |
| Koordination | Orchestrator managed | Shared Task List, self-organizing | Kontrolliertes Routing → **Subagents** |
| Upgrade-Pfad | → Agent Teams möglich | - | Subagents jetzt, Teams wenn nötig |

### Manager Pattern (Atomic.Net-Prinzip)

> **Der Orchestrator coded NIE. Er delegiert NUR.** Jeder Agent hat klar definierte Grenzen und Tools. Der Review-Loop wird vom Orchestrator gesteuert, nicht von den Agents selbst.

Referenz: [SteffenBlake/Atomic.Net](https://github.com/SteffenBlake/Atomic.Net) — Manager Agent Pattern

### Open-Source Referenz-Repos (Research 10. Feb 2026)

Existierende Repos die ähnliche Dinge tun. Was wir übernehmen, was nicht, und warum.

#### Was wir nutzen können ✅

| Repo | Stars | Was wir übernehmen | Warum relevant |
|------|-------|-------------------|----------------|
| [claude-hub](https://github.com/claude-did-this/claude-hub) | 344 | Webhook → Claude Code Pipeline, HMAC Signatur-Validierung, Session Management, Authorized Users Allowlist | Macht ~80% von dem was wir bauen, nur in TypeScript. Unser USP: Knowledge Layer (Pinecone MCP) + Dashboard |
| [claude-code-hooks-multi-agent-observability](https://github.com/disler/claude-code-hooks-multi-agent-observability) | 1038 | Dashboard-Architektur, Event-Schema, Hook-Scripts, WebSocket Live-Updates, Agent-Session-Tracking | Genau das Dashboard das wir mit HTMX bauen wollen — nur in Vue 3. Event-Schema + SQLite-Logging 1:1 übertragbar |
| [e2b-dev/claude-code-fastapi](https://github.com/e2b-dev/claude-code-fastapi) | 17 | FastAPI + Claude Code Skeleton, `POST /chat` + `POST /chat/{session}` Resume, MCP-Config | Exakt unser Tech-Stack als Minimal-Skeleton. Session-Resume-Pattern direkt übernehmbar |
| [anthropics/claude-code-security-review](https://github.com/anthropics/claude-code-security-review) | 2967 | PR-Review Prompt-Templates (`prompts.py`), False-Positive-Filtering, Diff-Aware Scanning | Offizielles Anthropic Repo. Prompt-Patterns für unseren Review Agent Gold wert |
| [doppelganger](https://github.com/dannyl1u/doppelganger) | 22 | Duplicate Detection mit Vector DB, Cosine Similarity, GitHub App Webhook | Vinnie's Original-Ask. Zeigt wie MiniLM + ChromaDB Duplicates findet. Wir nutzen Pinecone statt ChromaDB |
| [github-issues-analyzer](https://github.com/sharjeelyunus/github-issues-analyzer) | 1 | FastAPI + SQLite + Embeddings + Priority/Severity Prediction | Unser Stack in klein. FastAPI + SQLite Pattern bestätigt unsere Architektur-Entscheidung |

#### Was wir NICHT übernehmen ❌

| Feature | Repo | Warum nicht |
|---------|------|-------------|
| Docker Container pro Request | claude-hub | Overkill für MVP. Wir laufen direkt auf Azure VM. Phase 2 Option |
| TypeScript/Express | claude-hub | Wir sind Python/FastAPI — C++ Team versteht Python besser |
| Vue 3 Frontend | observability | Wir nutzen HTMX + Jinja2 — leichter, kein Build-Step, reicht für PoC |
| E2B Sandbox | e2b-dev | Wir haben Azure VM mit $5000 Credits. Extra Service = extra Kosten |
| Agent Teams | observability | Entscheidung steht: Subagents (sequentiell, günstiger). Upgrade-Pfad bleibt |
| ChromaDB | doppelganger | Will hat Pinecone MCP — kein Grund für zweite Vector DB |

#### Übersehen aber WICHTIG — jetzt im Plan ⚠️

| Feature | Inspiration von | Warum wichtig | Wo im Plan |
|---------|----------------|---------------|------------|
| **Authorized Users Allowlist** | claude-hub | Ohne das kann JEDER GitHub-User unsere Agents triggern! Security-kritisch | Kapitel 2: FastAPI Server |
| **Repo-Caching** | claude-hub | Repo muss nicht bei jedem Agent-Spawn neu geclont werden → Sekunden statt Minuten | Kapitel 3: Agent Spawner |
| **False-Positive-Filtering** | anthropics/security-review | Review Agent braucht Filter für Low-Impact Findings, sonst Noise | Kapitel 3: Agent Spawner (Review Agent) |

> **Unser USP gegenüber ALLEN Repos:** Keines hat eine **Knowledge Mining Pipeline mit Pinecone MCP + Fidelity Gates + domänenspezifischem C++/Clang-Wissen**. Die bauen alle generische Agents. Wir bauen einen Agent der PRs reviewt wie Richard Smith.

### NEU: Database-First Knowledge Layer (TheAuditor-Pattern)

| Datenbank | Zweck | Query-Typ |
|-----------|-------|-----------|
| **SQLite** (strukturiert) | Exakte Lookups, Statistiken, Beziehungen | Deterministisch — LLM kann NICHT halluzinieren |
| **Pinecone** (semantisch) | Ähnlichkeitssuche, Pattern-Matching | Probabilistisch — Kontext für nuanciertes Verständnis |

**Fidelity Gates:** An jeder Pipeline-Grenze (Scrape → Index → Embed) wird Datenintegrität per Manifest-Receipt-System verifiziert. Garantie: 0% Datenverlust.

Referenz: [TheAuditor v2](https://github.com/TheAuditorTool/Auditor) — AGPL-3.0, verifizierte Accuracy auf 834k+ Code-Elementen

---

## MVP: Was gebaut wird

### Gesamtarchitektur (auf Azure VM)

```
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║                   🖥️  AGENT DASHBOARD (Frontend)                 ║
║                      HTMX + TailwindCSS                          ║
║                                                                  ║
║   ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐  ║
║   │  Active    │  │  Realtime  │  │   Agent    │  │  System  │  ║
║   │  Agents    │  │   Logs     │  │  Steps /   │  │ Health + │  ║
║   │  Status    │  │  Stream    │  │   Chat     │  │  Costs   │  ║
║   └────────────┘  └────────────┘  └────────────┘  └──────────┘  ║
║                                                                  ║
╚══════════════════════════════╤═══════════════════════════════════╝
                               │ WebSocket
╔══════════════════════════════╧═══════════════════════════════════╗
║                                                                  ║
║                ORCHESTRATION SERVER (FastAPI)                     ║
║                                                                  ║
║   ┌──────────────────────────────────────────────────────────┐   ║
║   │                    WEBHOOK ROUTER                         │   ║
║   │                                                          │   ║
║   │   issue_comment   ──→  Knowledge ──→ Coding ──→ Review   │   ║
║   │   check_run_fail  ──→  CI-Fixer Agent                    │   ║
║   │   pull_request    ──→  Review Agent                      │   ║
║   └──────────────────────────┬───────────────────────────────┘   ║
║                              │                                   ║
║            ┌─────────────────┴─────────────────┐                 ║
║            │                                   │                 ║
║   ┌────────▼─────────┐            ┌────────────▼────────────┐    ║
║   │  AGENT SPAWNER   │            │     LOG COLLECTOR       │    ║
║   │                  │            │                         │    ║
║   │  claude -p "..." │            │  ┌───────────────────┐  │    ║
║   │  --output json   │            │  │ • Prompt sent     │  │    ║
║   │  --continue      │            │  │ • Output received │  │    ║
║   │  --allowedTools  │            │  │ • Tools used      │  │    ║
║   │  --resume <sid>  │            │  │ • Duration (ms)   │  │    ║
║   │                  │            │  │ • Token cost ($)  │  │    ║
║   └────────┬─────────┘            │  └───────────────────┘  │    ║
║            │                      │  SQLite + WebSocket     │    ║
║            │                      └─────────────────────────┘    ║
║            │                                                     ║
║   ┌────────▼─────────────────────────────────────────────────┐   ║
║   │                                                          │   ║
║   │                AGENT POOL (Claude Code CLI)              │   ║
║   │                                                          │   ║
║   │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │   ║
║   │   │  KNOWLEDGE   │  │   CODING     │  │   REVIEW     │  │   ║
║   │   │   AGENT      │  │    AGENT     │  │    AGENT     │  │   ║
║   │   │              │  │              │  │              │  │   ║
║   │   │  • MCP Query │  │  • Read/Edit │  │  • Read/Grep │  │   ║
║   │   │  • Summarize │  │  • Bash/Git  │  │  • Validate  │  │   ║
║   │   │  • Context   │  │  • Create PR │  │  • ALL CLEAR │  │   ║
║   │   └──────────────┘  └──────────────┘  └──────┬───────┘  │   ║
║   │                                              │          │   ║
║   │                         ┌─────── NO ─────────┘          │   ║
║   │                         │  (Loop back to Coding Agent)  │   ║
║   │                         ▼                               │   ║
║   └──────────────────────────────────────────────────────────┘   ║
║                              │                                   ║
║            ┌─────────────────┴─────────────────┐                 ║
║            │                                   │                 ║
║   ┌────────▼─────────┐            ┌────────────▼────────────┐    ║
║   │  SESSION STORE   │            │      MCP SERVER         │    ║
║   │                  │            │                         │    ║
║   │  ~/.claude/      │            │  Pinecone Vector DB     │    ║
║   │  --continue      │            │  C++ / Boost / Clang    │    ║
║   │  --resume <sid>  │            │  Will's npm Package     │    ║
║   └──────────────────┘            └─────────────────────────┘    ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝

                    ┌──────────────────────┐
                    │   GITHUB TEST-REPO   │
                    │                      │
                    │  Issue erstellt  ────────→  Webhook POST
                    │  CI failed      ────────→  Webhook POST
                    │  PR created     ────────→  Webhook POST
                    │                      │
                    │  ←──── PR/Comment ───────  Agent Result
                    └──────────────────────┘
```

### Tech-Stack

```
Backend:
├── Python 3.11+
├── FastAPI (Webhook-Server + WebSocket + Dashboard API)
├── SQLite (Agent-Logs, Sessions, Run-History)
├── Claude Code CLI (subprocess.Popen, JSON output)
└── uvicorn (ASGI Server)

Frontend (Agent Dashboard):
├── HTMX (für PoC ausreichend, kein React-Overhead)
├── TailwindCSS (schnelles Styling)
├── WebSocket Client (Live-Log-Stream)
└── Chart.js (Kosten-Übersicht, optional)

Infrastructure:
├── Azure VM (B2ms, Ubuntu 22.04, $5000 MS Credits)
├── nginx (Reverse Proxy + HTTPS)
├── systemd (FastAPI + MCP als Services)
└── Let's Encrypt (SSL Zertifikat)
```

### Was der MVP bei der Demo zeigen muss

| # | Demonstration | Warum wichtig |
|---|---------------|---------------|
| 1 | **GitHub Event → Server reagiert** | Beweist: Webhook-Infrastruktur funktioniert |
| 2 | **Agent spawnt in Sekunden** | Beweist: Kein 2-5 min Cold Start mehr |
| 3 | **MCP-Query funktioniert** | Beweist: Pinecone-Wissensbasis ist angebunden |
| 4 | **Multi-Agent arbeitet getrennt** | Beweist: Orchestration Layer funktioniert |
| 5 | **Session wird resumed** | Beweist: State-Persistence über Events hinweg |
| 6 | **Ergebnis landet auf GitHub** | Beweist: Full-Loop von Event bis PR/Kommentar |
| 7 | **Dashboard zeigt alles live** | Beweist: Volle Überwachung + Debugging möglich |

### Kosten-Modell: Was permanent läuft vs. on-demand

| Komponente | Laufzeit | Kosten/Monat | Bezahlt durch |
|---|---|---|---|
| Azure VM (B2ms) | 24/7 | ~$60 | **$5000 MS Credits** |
| FastAPI Server | 24/7 | $0 (auf VM) | Credits |
| MCP Server | 24/7 | $0 (auf VM) | Credits |
| Claude Code | On-demand | Token-basiert | Anthropic API Key |
| Azure Blob Storage | Build-Cache | ~$5 | Credits |
| **TOTAL Server-Kosten** | | **~$65/Monat** | **Credits reichen ~76 Monate** |

---

## $5000 Microsoft Azure Startup Credits - Strategie

### Verfügbare Azure Services

| Service | Einsatz | Geschätzte Kosten |
|---------|---------|-------------------|
| **Azure VM (B2ms)** | Webhook-Server + Claude Code Runtime | ~$60/Monat |
| **Azure Blob Storage** | Build-Cache für Boost/Clang | ~$5/Monat |
| **Azure OpenAI Service** | Günstiges LLM für Knowledge-Agent (GPT-4o) | ~$20-100/Monat (tokenbasiert) |
| **Azure Key Vault** | Sichere API-Key Speicherung | ~$1/Monat |
| **Azure Monitor** | Logging & Monitoring der Agents | ~$5/Monat |

### Hybrid-LLM-Strategie (Kosten-Optimierung)

```
Manager Agent (Claude Code CLI - orchestriert)
    |
    +-- Knowledge Agent → Azure OpenAI GPT-4o  [GÜNSTIG]
    |   Aufgabe: Pinecone querien, Zusammenfassen
    |   Warum günstig: Einfache Retrieval-Task, kein Coding
    |
    +-- Coding Agent → Claude Sonnet/Opus     [TEUER aber nötig]
    |   Aufgabe: Code generieren, Fixes implementieren
    |   Warum teuer: Braucht beste Qualität für C++ Code
    |
    +-- Review Agent → Claude Sonnet          [MITTEL]
        Aufgabe: Code-Review, Validierung
        Warum mittel: Review braucht Qualität, aber weniger Tokens
```

**Vorteil:** Knowledge-Agent läuft am häufigsten (bei jedem Event), ist aber der günstigste. Die teuren Agents (Coding/Review) laufen nur wenn wirklich gecodet wird.

---

## Deliverables

### Für das Mid-February Meeting

| # | Deliverable | Format | Status |
|---|-------------|--------|--------|
| 1 | **Architektur-Dokument** | RESEARCH-CLI-HOOKS-ARCHITECTURE (DE + EN) | ✅ Fertig |
| 2 | **CLI Vergleich** | Cursor CLI vs Claude Code, 9 Dimensionen | ✅ Fertig |
| 3 | **Hook-Systeme Analyse** | Cursor 8 Events vs Claude Code 15 Events | ✅ Fertig |
| 4 | **Agent-Architektur** | Swarm vs Subagents vs Agent Teams Vergleich | ✅ Fertig |
| 5 | **Consultant Paper** | Professionelles Architektur-Proposal (Pyramid Principle) | ✅ Fertig |
| 6 | **Fidelity Architecture Proposal** | Database-First + Manifest-Receipt (TheAuditor-Pattern) | ✅ Fertig |
| 6b | **Q&A Architecture Decisions** | 6 Kernfragen beantwortet (Englisch), Cursor CLI Korrektur | ✅ Fertig |
| 7 | **Funktionierender MVP** | Webhook-Server auf Azure mit Multi-Agent | 🔴 TODO |
| 8 | **Live Demo** | Test-Repo → Issue → Agent reagiert live | 🔴 TODO |
| 9 | **Kosten-Kalkulation** | Token-Kosten pro Agent-Typ, Server-Kosten | 🟡 Teilweise |

### Für Phase 2 (nach Meeting)

| # | Deliverable | Abhängig von |
|---|-------------|--------------|
| 1 | Production Migration Guide | Meeting-Feedback |
| 2 | Agent Teams Upgrade (wenn nötig) | Subagent-Limitationen |
| 3 | CI-Cache Integration | Will's Build-Cache Setup |
| 4 | Monitoring Dashboard | Azure Monitor Setup |

---

## Timeline

| Datum | Milestone | Status |
|-------|-----------|--------|
| 03. Feb 2026 | Huddle mit Will Pak - Scope definiert | ✅ |
| 04-07. Feb 2026 | Research Phase (CLI, Hooks, Architektur) | ✅ |
| 09. Feb 2026 | Tech-Entscheidung: FastAPI + Claude Code CLI + Dashboard | ✅ |
| **09. Feb 2026** | **MCP Zugang von Will anfragen** | ✅ Erhalten |
| 10. Feb 2026 | Azure VM aufsetzen (Ubuntu, nginx, systemd) | 🔴 TODO |
| 10-11. Feb 2026 | FastAPI Grundgerüst + Agent Spawner + SQLite Logging | 🔴 TODO |
| 11-12. Feb 2026 | Agent Dashboard (HTMX, WebSocket, Live-Logs) | 🔴 TODO |
| 12-13. Feb 2026 | MCP Server integrieren + Agent-Routing Pipeline | 🔴 TODO |
| 13-14. Feb 2026 | Multi-Agent PoC: Knowledge → Coding → Review | 🔴 TODO |
| 14-15. Feb 2026 | End-to-End Test + Live Demo vorbereiten | 🔴 TODO |
| **~16. Feb 2026** | **Mid-February Meeting mit Will - LIVE DEMO** | 🔴 Geplant |
| Feb-Sep 2026 | Phase 2: Production Integration | ⏸️ Nach Meeting |

---

## Next Steps

### SOFORT (Heute/Morgen)
- [x] **Will anschreiben:** MCP Server Package + Zugang anfragen → ✅ ERHALTEN
- [ ] **Azure VM aufsetzen:** Ubuntu 22.04 B2ms mit Startup Credits
- [ ] **FastAPI Grundgerüst:** Webhook empfangen + Signatur validieren
- [ ] **Test-Repo erstellen:** Für die Live-Demo

### Diese Woche (bis 14. Feb)
- [ ] MCP Server auf Azure VM deployen (`npx -y @will-cppa/pinecone-read-only-mcp`)
- [ ] Claude Code CLI auf VM installieren + testen
- [ ] Agent-Routing: Event → Knowledge → Coding → Review Pipeline
- [ ] Session-Resume testen (--continue / --resume)
- [ ] End-to-End Test: Issue erstellen → Agent reagiert → Kommentar auf GitHub

### Vor dem Meeting (15. Feb)
- [ ] Live Demo 3x durchspielen (kein Risiko bei der Präsentation)
- [ ] Fallback-Plan falls MCP nicht rechtzeitig kommt (Mock-Daten)
- [ ] Kosten-Kalkulation finalisieren
- [ ] Präsentations-Talking-Points vorbereiten

### Offene Abhängigkeiten

| Abhängigkeit | Von wem | Status | Fallback |
|---|---|---|---|
| MCP Server Package | Will Pak | ✅ Erhalten | `@will-cppa/pinecone-read-only-mcp` |
| Pinecone API Zugang | Will Pak | ✅ Erhalten | API Key vorhanden (in `.env`, NICHT committen!) |
| Anthropic API Key | Eigener Account | 🟡 Vorhanden | - |
| Azure Credits | Eigene MS Credits | ✅ $5000 verfügbar | - |
| GitHub Test-Repo | Eigenes Setup | ✅ Kann selbst erstellen | - |

---

## Business-Strategie (Internal - NUR FÜR MICH)

### Verhandlungs-Position

**Hybrid-Move:** MVP mit eigenen Azure Credits bauen (kostet $0 Infrastruktur, nur meine Zeit). Bei der Live-Demo im Meeting aus Position der Stärke verhandeln.

> **Beim Meeting sagen:** *"This is a working prototype. The webhook server, the agent orchestration, the MCP integration - it all works. To take this to production and integrate it with your repos, that's Phase 2."*

### Phasen-basierte Abrechnung

| Phase | Scope | Zeitraum | Ballpark |
|-------|-------|----------|----------|
| **Phase 1** (Research + MVP) | Architektur-Design, CLI-Vergleich, funktionierender PoC auf Azure | Feb 3 - Feb 16 | €3.000-5.000 |
| **Phase 2** (Production) | MVP → Production Migration, Agent-Tuning, Integration mit ihren Repos | Feb-Apr 2026 | €10.000-20.000 |
| **Phase 3** (Ongoing) | Monitoring, Agent-Optimierung, neue Agent-Typen, Maintenance | Apr-Sep 2026 | €2.000-5.000/Monat |

### Warum diese Strategie funktioniert

1. **Leverage:** Ich habe einen funktionierenden MVP - die haben nichts Vergleichbares
2. **Azure Credits sind MEINE:** Die Infrastruktur gehört mir, nicht denen
3. **Lock-in:** Wenn der PoC funktioniert, ist es am einfachsten MICH weitermachen zu lassen
4. **Wert demonstriert:** Nicht "ich könnte vielleicht..." sondern "hier läuft es, wollt ihr weitermachen?"
5. **Non-Profit beachten:** C++ Alliance hat begrenztes Budget - Phasen-basiert ist besser als Big Bang

### Pricing Considerations

This is NOT a small project. Reference ranges:

| Scope | Ballpark |
|-------|----------|
| POC only (RAG on existing data) | €10k-20k |
| Full agent with GitHub integration | €30k-50k |
| Fine-tuning + ongoing maintenance | €50k-100k+ |

**Note:** C++ Alliance is non-profit, budget may be constrained. Focus on delivering value in phases.

#### Technical Approach

```
┌─────────────────────────────────────────────────────────────────┐
│                    DUPLICATE DETECTION PIPELINE                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐    ┌───────────────┐    ┌──────────────────┐     │
│  │ GitHub   │───▶│ Preprocessing │───▶│ Embedding Model  │     │
│  │ API      │    │ (Optional LLM)│    │ (OpenAI/Voyage)  │     │
│  └──────────┘    └───────────────┘    └────────┬─────────┘     │
│                                                 │               │
│                                                 ▼               │
│                                        ┌──────────────┐        │
│                                        │ Vector Store │        │
│                                        │ (NumPy/FAISS)│        │
│                                        └──────┬───────┘        │
│                                               │                 │
│  ┌──────────────────────────────────────────┐ │                 │
│  │         SIMILARITY MATRIX                │◀┘                 │
│  │  ┌───┬───┬───┬───┬───┐                  │                   │
│  │  │   │ 1 │ 2 │ 3 │...│   Issue i vs j   │                   │
│  │  ├───┼───┼───┼───┼───┤   Cosine Sim     │                   │
│  │  │ 1 │1.0│.23│.91│...│                  │                   │
│  │  ├───┼───┼───┼───┼───┤   Threshold:     │                   │
│  │  │ 2 │.23│1.0│.45│...│   > 0.85 = Alert │                   │
│  │  ├───┼───┼───┼───┼───┤                  │                   │
│  │  │ 3 │.91│.45│1.0│...│                  │                   │
│  │  └───┴───┴───┴───┴───┘                  │                   │
│  └──────────────────────────────────────────┘                   │
│                          │                                      │
│                          ▼                                      │
│                 ┌─────────────────┐                            │
│                 │ CSV Output      │                            │
│                 │ Issue A, B,     │                            │
│                 │ Similarity      │                            │
│                 └─────────────────┘                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Two Options Discussed

| Option | Approach | Pros | Cons |
|--------|----------|------|------|
| **A: Quick & Dirty** | Title + first 1000 chars → embeddings directly | Fast, cheap | Noisy, false positives |
| **B: Cleaned & Structured** | LLM extracts component/error/trigger first → then embeddings | Cleaner signal | Higher token cost, more setup |

**Decision:** Start with Option A on 100-200 issues as a test. Scale or switch to Option B based on results.

### ⏸️ Phase 2: WG21 Project (LATER)

**Objective:** TBD - Knowledge capture workflow with semantic comparison for C++ standards proposals.

**Notes:**
- Will discuss in huddle after Phase 1 POC
- Same embedding approach could work for matching proposals/papers
- Scope unclear - need to understand their GitHub-driven workflow

---

## Conversation Log

### Key Exchanges

**Vinnie's Requirements:**
> "Maybe. Whatever is the most effective and cheapest"
> "Find duplicates in these issues"
> "we have to get the issues first"

**Our Response Strategy:**
- No prices mentioned upfront (let client anchor first)
- Offered two clear options (A vs B)
- Proposed small test first (100-200 issues)
- Asked about scope (one-time vs ongoing)

### Messages Sent to Vinnie

1. **Technical Pipeline Diagram** - Showed the architecture
2. **Two Options** - Quick & Dirty vs Cleaned & Structured
3. **Test Proposal** - "Let me run Option A on 100-200 issues first"
4. **Scope Question** - "One-time cleanup or something ongoing?"
5. **Hybrid Search Mention** - For future enhancement

### Vinnie's Responses

- Confirmed interest: "we have to get the issues first"
- No budget mentioned yet
- No scope clarification yet

---

## Technical Details

### Embedding Costs (Estimates)

| Model | Cost per 1M tokens | Est. cost for 7k issues |
|-------|-------------------|------------------------|
| `text-embedding-3-small` | $0.02 | ~$0.10 |
| `text-embedding-3-large` | $0.13 | ~$0.65 |
| Voyage AI | Variable | TBD |

**Verdict:** Embedding costs are negligible. Main cost is time/labor.

### GitHub API Considerations

- **Rate Limit (no token):** 60 requests/hour
- **Rate Limit (with token):** 5,000 requests/hour
- **Recommendation:** Use personal access token for 7k issues

### Dependencies

```python
# Core
requests          # GitHub API
openai            # Embeddings
numpy             # Matrix math
pandas            # Data handling
scikit-learn      # Cosine similarity

# Optional
faiss-cpu         # Fast similarity search (if scaling)
```

---

## Decisions Made

| Decision | Rationale |
|----------|-----------|
| Start with Option A | Client wants "cheap and effective" - test first |
| No LLM preprocessing initially | Adds cost/complexity - validate need first |
| Test on 100-200 issues | Low risk, quick feedback loop |
| Use own GitHub token | Avoids asking client for credentials |
| No price mentioned | Let client anchor - stronger negotiation position |
| Focus on Clang first | Concrete deliverable, WG21 is more exploratory |

---

## Next Steps

### Immediate (Pending Client Go-Ahead)

- [ ] Get confirmation from Vinnie to start
- [ ] Set up project directory and environment
- [ ] Create GitHub issue scraper script
- [ ] Pull first 100-200 Clang issues
- [ ] Generate embeddings
- [ ] Compute similarity matrix
- [ ] Deliver initial CSV with results

### After POC Review

- [ ] Discuss results with Vinnie
- [ ] Decide: Scale to 7k issues or switch to Option B
- [ ] Discuss pricing based on scope
- [ ] Plan WG21 project kickoff

---

## Upsell Opportunities

1. **Hybrid Search** - Combine semantic + keyword matching for error codes
2. **Live System** - Webhook integration to check new issues against existing
3. **Clustering** - Group related issues (not just pairs)
4. **WG21 Project** - Separate engagement after Phase 1

---

## Files & Resources

### Project Files (To Be Created)

```
cursor-consulting/
└── projects/
    └── vinnie-cppalliance-duplicate-detection/
        ├── PROJECT-PLAN.md          # This file
        ├── scripts/
        │   ├── scrape_issues.py     # GitHub API scraper
        │   ├── generate_embeddings.py
        │   └── compute_similarity.py
        ├── data/
        │   ├── issues_raw.json      # Raw issue data
        │   └── duplicates.csv       # Results
        └── docs/
            └── conversation-log.md   # Full chat history
```

### External Resources

- [LLVM GitHub](https://github.com/llvm/llvm-project)
- [C++ Alliance GitHub](https://github.com/cppalliance)
- [OpenAI Embeddings API](https://platform.openai.com/docs/guides/embeddings)

---

## Budget & Pricing

**NOT DISCUSSED YET** - Waiting for client to indicate scope/budget first.

Potential pricing tiers (internal reference only):

| Tier | Scope | Ballpark |
|------|-------|----------|
| POC | 100 issues, basic CSV | €500-1,000 |
| Full Analysis | All 7k issues, Option A | €2,000-5,000 |
| Production System | Live duplicate detection | €10,000-25,000 |

---

## Notes

- Vinnie is technical - no need to oversimplify
- He's pragmatic - show results, not slides
- C++ Alliance is non-profit - budget may be limited
- This could be a good portfolio piece (open source contribution)

---

---

## Change Log

| Datum | Änderung |
|-------|----------|
| 04. Feb 2026 | Initial Plan erstellt nach Huddle mit Will Pak |
| 09. Feb 2026 | **MAJOR UPDATE:** MVP-Strategie hinzugefügt - Webhook-Server auf Azure bauen mit $5000 MS Credits. Arbeitsteilung klargestellt (SG = Architekt + PoC, Will = Infrastruktur + Production). Business-Strategie: Hybrid-Move mit Live-Demo als Verhandlungs-Leverage. |
| 09. Feb 2026 | **TECH-ENTSCHEIDUNG:** FastAPI + Claude Code CLI (subprocess) + Agent Dashboard. Frameworks (LangGraph/CrewAI) verworfen. Claude Code CLI hat alle nötigen Tools built-in. Dashboard mit HTMX + WebSocket für Live-Monitoring aller Agent-Runs. Inspiriert durch Michael Truell: "Cursor = Dashboard for working with agents." |
| 10. Feb 2026 | **TECH-UPDATE:** CLI subprocess → **Claude Agent SDK (Python)** — offizielles Anthropic SDK, native Python Integration, keine Subprocesses mehr. Gleiche Tools (Read, Edit, Bash, Git, MCP) aber als typisierte Python API. |
| 10. Feb 2026 | **CONSULTANT PAPER:** Professionelles Architektur-Proposal erstellt (McKinsey Pyramid Principle: Recommendation → Situation → Complication → Resolution). Client-facing Dokument mit 4-Layer-Architektur, Agent-Definitionen, Pipeline-Workflow, Fidelity Gates, Risk Assessment, Kosten-Modell, Success Criteria. Referenzen: OpenAI Agent Guide, Deloitte Agentic Enterprise, Atomic.Net Manager Pattern, TheAuditor v2. |
| 10. Feb 2026 | **ENTSCHEIDUNG: Subagents > Agent Teams.** Sequentielle Pipeline braucht kein Peer-to-Peer. Token-Kosten niedriger. Upgrade-Pfad zu Teams bleibt offen. Manager Pattern (Atomic.Net): Orchestrator coded NIE, delegiert NUR. |
| 10. Feb 2026 | **DATABASE-FIRST:** Hybrid SQLite (deterministisch) + Pinecone (semantisch) mit Fidelity Gates (Manifest-Receipt Reconciliation) an jeder Pipeline-Grenze. Adaptiert von TheAuditor v2. |
| 10. Feb 2026 | **Q&A DOKUMENT:** 6 Kernfragen beantwortet (Englisch). **KORREKTUR:** Cursor CLI indiziert NICHT — Indexing ist nur ein IDE-Feature (bestätigt durch Cursor Team: "Cursor CLI does not index codebase, this is only done by the IDE"). Die Entscheidung für Claude Code basiert auf: Python SDK, Built-in Subagents, 15 Hook Events — NICHT auf Indexing-Performance. |
| 10. Feb 2026 | **MCP ZUGANG ERHALTEN:** Will Pak hat MCP Server Package geliefert: `npx -y @will-cppa/pinecone-read-only-mcp`. Pinecone API Key vorhanden. Abhängigkeit gelöst — kein Fallback (FAISS) mehr nötig. |
| 10. Feb 2026 | **OPEN-SOURCE RESEARCH:** 7 Repos analysiert + geclont. claude-code-action (5592⭐) gefunden — Anthropic's eigener /dedupe Duplicate-Bot. Token-Kosten-Strategie aktualisiert mit offiziellen Anthropic Docs (Prompt Caching: 90% Ersparnis). 8 direkt kopierbare Python/FastAPI Code-Patterns dokumentiert in REFERENCE-REPOS-ANALYSIS.md. |
| 10. Feb 2026 | **ARCHITEKTUR-PIVOT: Built-in Orchestration.** Claude Code hat seit Opus 4.6 (5. Feb 2026) native Subagent-Orchestration via `.claude/agents/*.md` Dateien. Agent-Definitionen sind jetzt Markdown statt Python-Klassen. FastAPI nur noch für Webhook + Dashboard. Claude Code übernimmt: Subagent Spawning, Model Selection, Tool Routing, Context Isolation, MCP Routing, Pipeline-Koordination. **Halbiert unseren Code.** |
| 10. Feb 2026 | **RESEARCH ABGESCHLOSSEN.** Execution Blueprint erstellt (PROJECT-PLAN-SHORT.md). 8 Kapitel mit konkreten Befehlen und Copy-Paste Anleitungen. Alle Abhängigkeiten gelöst. Nächste Aktion: Ausführung, nicht Research. |

*Last Updated: February 10, 2026*



┌─────────────────────────────────────────────────────────────┐
│                    AGENT DASHBOARD (Frontend)                │
│                    Next.js / React / HTMX                   │
│                                                             │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐  │
│  │ Active    │ │ Real-time │ │ Agent     │ │ System    │  │
│  │ Agents    │ │ Logs      │ │ Chat/     │ │ Health    │  │
│  │ Status    │ │ Stream    │ │ Steps     │ │ Costs     │  │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘  │
│                        ▲ WebSocket                          │
└────────────────────────┼────────────────────────────────────┘
                         │
┌────────────────────────┼────────────────────────────────────┐
│              ORCHESTRATION SERVER (FastAPI)                  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                Webhook Router                        │   │
│  │  issue_comment  → Knowledge → Coding → Review       │   │
│  │  check_run_fail → CI-Fixer Agent                    │   │
│  │  pull_request   → Review Agent                      │   │
│  └─────────────────────────────────────────────────────┘   │
│           │                    │                            │
│  ┌────────▼────────┐ ┌───────▼─────────┐                  │
│  │ Agent Spawner   │ │ Log Collector   │                  │
│  │ (subprocess)    │ │ (SQLite + WS)   │                  │
│  │                 │ │                 │                  │
│  │ claude -p "..." │ │ Jeder Agent-Run │                  │
│  │ --output json   │ │ wird geloggt:   │                  │
│  │ --continue      │ │ - Prompt        │                  │
│  │ --allowedTools  │ │ - Output        │                  │
│  └────────┬────────┘ │ - Tools used    │                  │
│           │          │ - Duration      │                  │
│           │          │ - Token cost    │                  │
│           │          └─────────────────┘                  │
│  ┌────────▼─────────────────────────────────────────┐     │
│  │              AGENT POOL (Claude Code CLI)         │     │
│  │                                                   │     │
│  │  ┌─────────────┐ ┌─────────────┐ ┌────────────┐ │     │
│  │  │ Knowledge   │ │ Coding      │ │ Review     │ │     │
│  │  │ Agent       │ │ Agent       │ │ Agent      │ │     │
│  │  │             │ │             │ │            │ │     │
│  │  │ MCP Query   │ │ Read/Edit   │ │ Read/Grep  │ │     │
│  │  │ Summarize   │ │ Bash/Git    │ │ Validate   │ │     │
│  │  │ Context     │ │ Create PR   │ │ ALL CLEAR? │ │     │
│  │  └─────────────┘ └─────────────┘ └────────────┘ │     │
│  └───────────────────────────────────────────────────┘     │
│           │                                                │
│  ┌────────▼────────┐  ┌──────────────┐                    │
│  │ Session Store   │  │ MCP Server   │                    │
│  │ (~/.claude/)    │  │ (Pinecone)   │                    │
│  └─────────────────┘  └──────────────┘                    │
└────────────────────────────────────────────────────────────┘