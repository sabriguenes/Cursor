# Research: CLI-Vergleich, Hooks & Architektur-Analyse

**Datum:** 9. Februar 2026  
**Autor:** SG (Cursor Consultant)  
**Kontext:** C++ Alliance - AI Code Review Agent Projekt  
**Status:** Research Phase (Deadline: Mitte Februar 2026)

---

## Inhaltsverzeichnis

1. [Problemanalyse: Claude Code + GitHub Runner](#1-problemanalyse-claude-code--github-runner)
2. [Graphiti als Loesung fuer Session Persistence](#2-graphiti-als-loesung-fuer-session-persistence)
3. [Deep Research: Cursor CLI vs Claude Code CLI](#3-deep-research-cursor-cli-vs-claude-code-cli)
4. [Hook-Systeme: Cursor vs Claude Code](#4-hook-systeme-cursor-vs-claude-code)
5. [Webhook-Server Architektur](#5-webhook-server-architektur)
6. [Agent-Architektur: Swarm vs Multi-Agent vs Agent Teams](#6-agent-architektur-swarm-vs-multi-agent-vs-agent-teams)
7. [Webhook-Server: Wie bleiben Agents aktiv?](#7-webhook-server-wie-bleiben-agents-aktiv)
8. [Empfehlung & Naechste Schritte](#8-empfehlung--naechste-schritte)

---

## 1. Problemanalyse: Claude Code + GitHub Runner

### Aktuelle Architektur (aus Huddle mit Will Pak, 3. Feb 2026)

```
Human (GitHub UI)
    -> Issue Comment "@claude fix issue #188"
    -> GitHub Webhook triggered
    -> GitHub CI Workflow startet
        -> Runner wird allokiert (Ubuntu VM)
        -> npm install claude-code          <-- Cold Start
        -> claude -p "fix this issue"
            -> Claude liest Issue, Code, etc.
            -> Claude erstellt PR, pusht Commits
            -> CI Build laeuft (Kompilation, Tests)
            -> Wenn fehlschlaegt -> neuer Commit -> CI again
            -> Bis zu 50 Iterationen          <-- Loop-Problem
        -> Runner wird zerstoert              <-- State verloren
```

### Die 4 Pain Points und ihre Root Causes

#### Pain Point 1: Slow Startup (2-5 Minuten)

**Root Cause: GitHub Actions Runner = Ephemeral VM**

Bei JEDEM Trigger passiert folgendes:
1. GitHub muss einen Runner allokieren (30s - 2min Queue-Zeit)
2. Frische Ubuntu VM wird gestartet
3. Repository wird geklont (bei grossen C++ Repos: 30s-2min)
4. `npm install claude-code` - Node.js Runtime + Dependencies (~300MB)
5. Claude Code initialisiert sich (Context-Aufbau, Codebase-Scan, API-Handshake)

**Ergebnis:** 2-5 Minuten bevor der erste Token generiert wird.

#### Pain Point 2: Lange CI-Fix-Loops (2h pro Iteration x 50 Retries)

**Root Cause: C++ Kompilation + Stateless Iterations**

Eine einzelne Iteration:
1. Claude pusht einen Fix-Commit (30s)
2. GitHub CI Workflow wird getriggert
3. Runner-Allokation (1-2 min)
4. Dependencies installieren (Boost, Clang = massiv)
5. Kompilation des Projekts (10-60 min)
6. Test-Matrix laeuft (10-30 min)
7. Ergebnis zurueck an Claude

**Pro Iteration = 1-2 Stunden. Bei 50 Retries = Mehrere Tage.**

Verschlimmert durch: Claude hat KEINEN State von vorherigen Iterationen. Er weiss nicht was er schon versucht hat und macht moeglicherweise den gleichen Fix nochmal.

#### Pain Point 3: Kein MCP im CI-Runner

**Root Cause: Isolierte Laufzeitumgebung**

- LOKAL (funktioniert): Cursor -> MCP Server -> Pinecone Vector DB
- AUF GITHUB RUNNER (fehlt): GitHub CI -> Claude Code -> ??? -> Pinecone

Der CI-Agent der Boost-Bugs fixen soll hat keinen Zugang zur C++/Boost-Wissensbasis die Will's Team aufgebaut hat. Er arbeitet blind.

#### Pain Point 4: Keine Session Persistence

**Root Cause: CI-Workflow = Fire-and-Forget**

```
Iteration 1: Claude lernt "B2 Build-Flag X bricht Test Y"
  -> VM wird zerstoert -> Wissen weg

Iteration 2: Claude lernt das GLEICHE nochmal
  -> VM wird zerstoert -> Wissen weg

Iteration 3: Claude macht den GLEICHEN Fehler wie Iteration 1
```

### Kern-Problem in einem Satz

> Sie haben einen STATEFUL Agent (Claude Code) in eine STATELESS Umgebung (GitHub CI Runner) gepresst, die fuer kurzlebige Build-Jobs designed ist, nicht fuer langlebige iterative Agent-Arbeit.

---

## 2. Graphiti als Loesung fuer Session Persistence

### Was ist Graphiti?

[github.com/getzep/graphiti](https://github.com/getzep/graphiti) - Ein Open-Source Framework fuer temporale Knowledge Graphs, entwickelt von Zep. 22.6k GitHub Stars.

**Kernfeatures:**
- Real-Time Incremental Updates (kein Batch-Processing)
- Bi-Temporales Datenmodell (wann passierte es + wann wurde es erfasst)
- Hybrid Retrieval (Semantic + Keyword + Graph Traversal)
- Custom Entity Definitions (Pydantic Models)
- MCP Server enthalten

### Bewertung gegen die 4 Pain Points

| Pain Point | Loest Graphiti? | Bewertung |
|---|---|---|
| **Slow Startup (2-5 min)** | NEIN | Graphiti braucht selbst eine DB (Neo4j/FalkorDB). Macht Cold Starts schlimmer. |
| **Lange CI-Loops (~2h, 50 Retries)** | Minimal | Theoretisch weniger Retries wenn Agent sich erinnert. Aber die 2h CI-Laufzeit bleibt. |
| **Kein MCP fuer Pinecone** | NEIN (Ersatz, kein Connector) | Graphiti hat MCP Server, aber nutzt Neo4j/FalkorDB - NICHT Pinecone. Migration noetig. |
| **Session Persistence** | TEILWEISE | Semantisches Gedaechtnis ueber Sessions - ja. Aber kein voller Session-State. |

### Fazit Graphiti

Graphiti loest nur einen Bruchteil des Problems (semantisches Gedaechtnis). Die dicksten Pain Points - Cold Start und CI-Laufzeit - werden null beruehrt. Kann als **Ergaenzung** dienen, aber nicht als primaere Loesung.

---

## 3. Deep Research: Cursor CLI vs Claude Code CLI

### 3.1 Architektur & Philosophie

| Dimension | Cursor CLI (`cursor-agent`) | Claude Code (`claude`) |
|---|---|---|
| **Paradigma** | IDE-Extension als CLI | Terminal-first autonomer Agent |
| **Modelle** | Multi-Model: Claude 4.6 Opus, GPT-5.2, Gemini 3 Pro, Grok, Composer 1 | Anthropic-only: Sonnet 4.5, Opus 4.5/4.6, Haiku 4.5 |
| **Ausfuehrung** | Lokal auf der Maschine, kein Remote-Runner | Lokal ODER remote (GitHub Actions Runner) |
| **Laufzeitstart** | Instant - startet wie jeder CLI-Prozess | 2-5 min Cold Start auf CI-Runnern |

### 3.2 Session Persistence

**Claude Code:**
- `claude --continue` - letzte Conversation fortsetzen
- `claude --resume <id>` - spezifische Session wieder aufnehmen
- Voller State wird gespeichert: Conversation History, Tool Calls, File References, Working Directory, Tool Permissions
- Background-Prozesse ueberleben Sessions
- `CLAUDE.md` + Auto-Memory laden automatisch (bis 200 Zeilen)
- `.claude/rules/` fuer pfadspezifische Regeln

**Cursor CLI:**
- `cursor-agent resume` - letzte Session fortsetzen
- `cursor-agent --resume="chat-id"` - spezifische Session
- `cursor-agent ls` - alle Sessions auflisten
- Sessions in `~/.cursor/chats/` gespeichert
- Kein automatisches Resume, manuelles Chat-ID-Handling noetig
- Open Feature Request (#3846) fuer automatisches Session-Resume

**Verdict:** Claude Code gewinnt klar bei Session Persistence.

### 3.3 MCP Support

**Claude Code:**
- Voller MCP Support: stdio, HTTP/SSE, Remote Servers
- Pre-built: PostgreSQL, GitHub, Slack, AWS, Puppeteer
- MCP Tool Search, MCP Prompts, MCP Resources

**Cursor CLI:**
- MCP Support: stdio und SSE Transport
- Gleicher MCP-Stack wie der Cursor Editor
- Zugang zu Cursor's MCP Directory

**Verdict:** Beide unterstuetzen MCP. Fuer den Pinecone Use-Case braucht man so oder so einen Pinecone MCP Server.

### 3.4 CI/CD Integration

**Claude Code:**
- Offizieller GitHub Action: `anthropics/claude-code-action` (5.5k Stars)
- Bekannte Bugs: Exit Code 1 nach 300-400ms, CPU-Leaks (100%+ idle), Orphaned Processes (tagelang, $50-100 API-Kosten)
- Cold Start: npm install + Runner-Allokation

**Cursor CLI:**
- GitHub Actions Integration dokumentiert
- `cursor-agent -p "prompt" --output-format=text --force` fuer headless Mode
- Kein eigener Runner noetig - laeuft als normaler CLI-Prozess
- Parallel Agents ueber Git Worktrees (bis zu 8)

**Verdict:** Cursor CLI hat strukturellen Vorteil bei CI-Reliability.

### 3.5 Multi-Agent / Parallel Execution

**Claude Code:**
- Agent Teams (Opus 4.6): Multiple Instanzen arbeiten kollaborativ
- Task Tool: Built-in Sub-Agents mit isolierten Kontexten
- `.claude/agents/` fuer persistente Spezialisten
- Max ~10 parallele Sub-Agents

**Cursor CLI:**
- Parallel Agents (Cursor 2.0): Bis zu 8 Agents gleichzeitig
- Git Worktrees als Isolations-Mechanismus
- Subagents ueber Shell spawnen mit `--model` Flag
- Fan-out/Fan-in Pattern

**Verdict:** Claude Code ist weiter bei autonomer Multi-Agent Koordination.

### 3.6 Pricing

| Plan | Cursor | Claude Code |
|---|---|---|
| **Free** | Hobby: 50 Premium Requests/Monat | Kein Free Tier |
| **$20/Monat** | Pro: $20 Credit, alle Modelle | Pro: 45 Msgs/5h, Sonnet 4.5 |
| **$60/Monat** | Pro+: Background Agents | - |
| **$100/Monat** | - | Max 5x: Opus 4.5 |
| **$200/Monat** | Ultra: 20x Usage | Max 20x: Priority Opus |
| **API** | $0.25/1M + Model-Kosten | Sonnet: $3/$15, Opus: $15/$75 per 1M |

**Token-Effizienz:** Claude Code braucht 5.5x weniger Tokens fuer aequivalente Tasks (33k vs 188k).

### 3.7 Performance

| Metrik | Cursor CLI | Claude Code |
|---|---|---|
| Autocomplete-Speed | Sub-second | N/A |
| Refactoring-Speed | 3-8 min (interaktiv) | 2-5 min (autonom) |
| Token-Effizienz | ~188k Tokens/Task | ~33k Tokens/Task |
| Context Window | 200k default, 1M Max | 200k default, 1M moeglich |
| Code-Qualitaet | Kein signifikanter Unterschied | Kein signifikanter Unterschied |

### 3.8 Security

**Claude Code:** OS-level Sandboxing mit gVisor-class Isolation, Filesystem + Network Isolation, 4 Permission Modes, 84% weniger Permission-Prompts.

**Cursor CLI:** Shell Mode mit Safety Checks, "Security safeguards still evolving" (Beta).

**Verdict:** Claude Code hat das ausgereiftere Security-Model.

### 3.9 Gesamtbewertung fuer C++ Alliance Use-Case

| Pain Point | Cursor CLI | Claude Code | Winner |
|---|---|---|---|
| **Slow Startup** | Instant (lokaler Prozess) | 2-5 min auf CI-Runnern | **Cursor CLI** |
| **CI Fix Loops** | Headless Mode, schneller Turnaround | Maechtig aber buggy | **Cursor CLI** |
| **MCP Support** | Voller MCP Support | Voller MCP Support | **Tie** |
| **Session Persistence** | Basis-Resume | Voller State-Persistence | **Claude Code** |

---

## 4. Hook-Systeme: Cursor vs Claude Code

### 4.1 Uebersicht

| Feature | Cursor Hooks | Claude Code Hooks |
|---|---|---|
| **Config-Datei** | `.cursor/hooks.json` | `.claude/settings.json` |
| **Hook-Typen** | 1 Typ: Command | 3 Typen: Command, Prompt, Agent |
| **Anzahl Events** | ~8 Events | 15 Events |
| **Blocking** | Teilweise | Volle Kontrolle (Exit Codes + JSON) |
| **MCP-Hooks** | Nein | Ja (`mcp__server__tool` Matcher) |
| **Async/Background** | Nein | Ja (`async: true`) |
| **Subagent-Hooks** | Nein | Ja (`SubagentStart`, `SubagentStop`) |
| **Agent Teams** | N/A | `TeammateIdle`, `TaskCompleted` |
| **Interaktives Menu** | Nein | `/hooks` Command |

### 4.2 Claude Code: Alle 15 Hook Events

```
SESSION-LIFECYCLE:
+-- SessionStart         -> Session beginnt/resumed
+-- SessionEnd           -> Session endet
+-- PreCompact           -> Vor Context-Komprimierung

USER-INTERACTION:
+-- UserPromptSubmit     -> Bevor Prompt verarbeitet wird

TOOL-LIFECYCLE:
+-- PreToolUse           -> VOR Tool-Ausfuehrung (kann BLOCKEN)
+-- PermissionRequest    -> Bei Permission-Dialog
+-- PostToolUse          -> NACH erfolgreicher Tool-Ausfuehrung
+-- PostToolUseFailure   -> NACH fehlgeschlagener Tool-Ausfuehrung

AGENT-LIFECYCLE:
+-- SubagentStart        -> Subagent wird gespawnt
+-- SubagentStop         -> Subagent fertig
+-- Stop                 -> Claude hoert auf zu antworten
+-- TeammateIdle         -> Agent-Team Member wird idle
+-- TaskCompleted        -> Task wird als erledigt markiert

NOTIFICATIONS:
+-- Notification         -> Claude sendet Benachrichtigung
```

### 4.3 Die 3 Hook-Typen von Claude Code

#### Command Hook (auch bei Cursor vorhanden)
Shell-Skript das JSON via stdin bekommt:
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

#### Prompt Hook (nur Claude Code)
Ein LLM bewertet ob die Aktion erlaubt ist:
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

#### Agent Hook (nur Claude Code)
Ein Subagent mit Tools (Read, Grep, Glob) wird gespawnt:
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

- `Exit 0` = Aktion erlauben (optional JSON-Output)
- `Exit 2` = Aktion BLOCKEN (stderr wird Claude als Error gezeigt)
- `Anderer Exit` = Non-blocking Error

### 4.5 Relevanz fuer C++ Alliance

| Hook | Use Case |
|---|---|
| `SessionStart` | Automatisch MCP/Pinecone verbinden, Git-Status laden |
| `PreToolUse` + Bash | Dangerous Commands blocken (`rm -rf`, `git push --force`) |
| `PostToolUse` + Edit | Auto-Formatter (clang-format) nach Datei-Aenderung |
| `Stop` (Agent Hook) | Review-Agent prueft ob Tests passen BEVOR Claude "fertig" sagt |
| `SubagentStop` | Ergebnisse paralleler Agents validieren |
| `TaskCompleted` | Verhindern dass Task als "done" markiert wird ohne CI-Success |

**Besonders wichtig:** Der `Stop`-Hook mit Agent-Typ verhindert dass Claude sich als "fertig" erklaert, bis ein Subagent bestaetigt hat dass die Tests laufen. Das reduziert die 50-Retry-Loops drastisch.

---

## 5. Webhook-Server Architektur

### Was ist ein Webhook-Server?

Ein eigener Server im Internet, der auf HTTP-Requests wartet. Bei GitHub Webhooks:

1. GitHub schickt HTTP POST an die Server-URL bei Events (Issue, PR, CI-Fail)
2. Server empfaengt, validiert Signatur (Sicherheit)
3. Server fuehrt Aktion aus (z.B. Claude Code starten)

### Warum loest das die Probleme?

| Problem | GitHub CI Runner | Webhook Server |
|---|---|---|
| Cold Start | 2-5 min (VM + npm install) | Instant (Prozess laeuft permanent) |
| State | Weg nach jedem Run | Persistent (Server lebt weiter) |
| MCP | Muss pro Run installiert werden | Laeuft permanent neben dem Agent |
| Build-Cache | Begrenzt (GitHub Cache Actions) | Voller lokaler Cache |

### Aufbau

```
GitHub Repository
    |
    v (Webhook: issue_comment, pull_request, check_run)
    |
Webhook Server (Hetzner/AWS/etc.)
    |
    +-- Express.js/FastAPI (empfaengt Events)
    +-- Claude Code SDK (permanent laufend)
    +-- MCP Server (Pinecone-Verbindung)
    +-- Self-hosted Runner (lokale Builds)
    +-- Build-Cache (Boost, Clang vorgebaut)
```

### Vorteile gegenueber aktueller Architektur

- **Instant Response**: Agent reagiert in Sekunden, nicht Minuten
- **Session Persistence**: `claude --continue` funktioniert weil der Prozess lebt
- **MCP immer verfuegbar**: Pinecone-Wissensbasis permanent connected
- **Build-Cache**: Boost/Clang vorgebaut, nur Delta-Kompilation
- **Kosten-Kontrolle**: Kein Runner-Minute-Verbrauch auf GitHub

---

## 6. Agent-Architektur: Swarm vs Multi-Agent vs Agent Teams

### 6.1 Die drei Paradigmen

#### Swarm (OpenAI-Stil)
- Viele gleichartige Agents die sich selbst organisieren
- Kein fester Leader, emergente Koordination
- Gut fuer: homogene Tasks (z.B. 100 PRs parallel reviewen)
- Schlecht fuer: komplexe Workflows mit verschiedenen Rollen

#### Multi-Agent / Subagents (Claude Code Built-in)
- Ein Haupt-Agent spawnt spezialisierte Sub-Agents
- Sub-Agents berichten zurueck an den Haupt-Agent
- Eigener Context pro Sub-Agent, Ergebnis wird zusammengefasst
- Gut fuer: fokussierte Tasks wo nur das Ergebnis zaehlt
- Token-Kosten: Niedrig (Ergebnis wird zusammengefasst)

#### Agent Teams (Claude Code, neu mit Opus 4.6)
- Ein Lead koordiniert unabhaengige Teammates
- Teammates kommunizieren DIREKT miteinander (Peer-to-Peer)
- Shared Task List mit Self-Coordination
- Gut fuer: komplexe Arbeit die Diskussion und Zusammenarbeit erfordert
- Token-Kosten: HOCH (jeder Teammate = eigene Claude-Instanz)

### 6.2 Referenz-Architektur: Atomic.Net Manager Pattern

Quelle: [github.com/SteffenBlake/Atomic.Net](https://raw.githubusercontent.com/SteffenBlake/Atomic.Net/refs/heads/main/.github/agents/manager.agent.md)

**Kern-Prinzip: Der Manager coded NIE selbst. Er delegiert NUR.**

```
Manager Agent (Orchestrator)
    |
    |-- FORBIDDEN: explore, task, oder andere Agents aufrufen
    |-- ONLY JOB: Delegieren an die 5 spezialisierten Agents
    |
    +-- tech-lead
    |   Rolle: Requirements aus Issues -> Sprint-Files erstellen
    |   Trigger: Nur wenn explizit angefragt
    |   Output: Sprint-File (muss von Mensch reviewed werden)
    |
    +-- senior-dev
    |   Rolle: Implementierung, Bug-Fixes, Test-Reparatur
    |   Trigger: Nach Sprint-File Approval oder direkte Bug-Requests
    |   Output: Code-Aenderungen
    |
    +-- benchmarker
    |   Rolle: Performance-Benchmarks erstellen und ausfuehren
    |   Trigger: Nur auf explizite Anfrage
    |   Output: Benchmark-Ergebnisse
    |
    +-- profiler
    |   Rolle: Profiling und Tracing spezifischer Code-Bereiche
    |   Trigger: Nur auf explizite Anfrage
    |   Output: Performance-Analyse
    |
    +-- code-reviewer
        Rolle: Extensives Code-Review JEDER Aenderung
        Trigger: NACH jeder Arbeit eines "Developer"-Agents
        Output: Review mit Feedback oder "100% ALL CLEAR"
```

**Kritische Regeln:**
1. Code-Reviewer wird NACH JEDER Aenderung aktiviert
2. Bei JEDEM Feedback (egal wie klein) -> zurueck an Developer
3. Loop endet ERST wenn: ALLE Tests passen UND Review = 100% ALL CLEAR
4. KEINE Zeitlimits - Agent nutzt 100% seines Token-Limits
5. Arbeit ist NICHT fertig bis alles gruen ist

### 6.3 Uebersetzung in Claude Code Architektur

#### Option A: Subagents (einfacher, guenstiger)

```json
// .claude/agents/manager.md
---
name: manager
description: Orchestriert spezialisierte Agents fuer C++ Alliance
tools: ['custom-agent']
---

DEINE EINZIGE AUFGABE: Delegiere an diese Agents:
1. knowledge-agent: Queried MCP/Pinecone fuer C++ Boost Kontext
2. coding-agent: Implementiert Fixes basierend auf Knowledge + Issue
3. review-agent: Prueft JEDEN Fix auf Korrektheit

WORKFLOW:
1. Issue kommt rein -> knowledge-agent holt relevanten Kontext
2. coding-agent bekommt Kontext + Issue -> implementiert Fix
3. review-agent prueft den Fix
4. Bei Feedback -> zurueck zu coding-agent
5. Loop bis review-agent "ALL CLEAR" gibt
6. ERST DANN: Push und PR erstellen
```

#### Option B: Agent Teams (maechtig, teuer)

```
Lead Agent (Manager)
    |
    +-- Teammate: knowledge-researcher
    |   - Queried Pinecone via MCP
    |   - Findet aehnliche Issues/Fixes
    |   - Kommuniziert direkt mit coding-dev
    |
    +-- Teammate: coding-dev
    |   - Implementiert Fixes
    |   - Bekommt Kontext vom knowledge-researcher
    |   - Wird vom code-reviewer gechallenged
    |
    +-- Teammate: code-reviewer
        - Prueft ALLE Aenderungen
        - Challenged den coding-dev direkt
        - Gibt erst frei wenn alles sauber ist
```

### 6.4 Empfehlung fuer C++ Alliance

**START mit Subagents (Option A):**
- Einfacher aufzusetzen
- Guenstigere Token-Kosten
- Ausreichend fuer den MVP
- 3 Agents: knowledge, coding, review

**SPAETER upgraden auf Agent Teams (Option B) wenn:**
- Subagents an Grenzen stossen (z.B. coding-agent braucht Rueckfragen an knowledge-agent waehrend der Arbeit)
- Budget fuer hoehere Token-Kosten vorhanden
- Komplexere Tasks die Peer-to-Peer Kommunikation erfordern

---

## 7. Webhook-Server: Wie bleiben Agents aktiv?

### 7.1 Die Antwort: Agents sind NICHT 24/7 aktiv

**Claude Code ist KEIN Daemon.** Es ist ein CLI-Prozess der startet, arbeitet, und sich beendet.

**ABER: Der Webhook-Server ist 24/7 aktiv.**

Die Architektur ist wie ein Arzt im Bereitschaftsdienst:
- Der Server ist 24/7 ERREICHBAR (Express/FastAPI Prozess)
- Claude Code wird ON-DEMAND gespawnt wenn ein Webhook reinkommt
- Sessions werden mit `--continue`/`--resume` wiederhergestellt
- MCP Server laeuft permanent als separater Prozess

### 7.2 Architektur-Diagramm

```
                    PERMANENT LAUFEND (24/7)
                    =======================
                    
GitHub ──webhook──> Webhook Server (FastAPI/Express)
                         |
                         +-- MCP Server (Pinecone) [permanent]
                         +-- Build-Cache (Boost/Clang) [auf Disk]
                         +-- Session Store (~/.claude/) [persistent]
                         
                    ON-DEMAND GESTARTET (pro Event)
                    ===============================
                    
                    Webhook empfangen
                         |
                         v
                    claude -p "Fix issue #188" \
                      --continue \
                      --allowedTools "Read,Edit,Bash" \
                      --output-format json
                         |
                         +-- Subagent: knowledge (queried MCP)
                         +-- Subagent: coding (implementiert)
                         +-- Subagent: review (prueft)
                         |
                         v
                    Ergebnis -> GitHub API -> PR/Kommentar
                    
                    Claude-Prozess beendet sich
                    Session-State bleibt in ~/.claude/
```

### 7.3 Pseudocode: Webhook-Server

```python
# server.py (FastAPI - laeuft 24/7)
from fastapi import FastAPI, Request
import subprocess
import json
import hmac

app = FastAPI()
WEBHOOK_SECRET = os.environ["GITHUB_WEBHOOK_SECRET"]
SESSION_MAP = {}  # issue_id -> claude session_id

@app.post("/webhook")
async def handle_webhook(request: Request):
    # 1. Signatur validieren
    payload = await request.body()
    signature = request.headers.get("X-Hub-Signature-256")
    verify_signature(payload, signature, WEBHOOK_SECRET)
    
    data = json.loads(payload)
    action = data.get("action")
    
    # 2. Event-Typ bestimmen
    if "issue" in data and action == "opened":
        await handle_new_issue(data)
    elif "check_run" in data and data["check_run"]["conclusion"] == "failure":
        await handle_ci_failure(data)

async def handle_new_issue(data):
    issue_id = data["issue"]["number"]
    repo = data["repository"]["full_name"]
    
    # 3. Claude Code spawnen mit Session-Resume
    cmd = [
        "claude", "-p",
        f"Fix issue #{issue_id} in {repo}. "
        f"Use the MCP server to query Pinecone for relevant C++ context. "
        f"Create a PR with the fix.",
        "--allowedTools", "Read,Edit,Bash,mcp__pinecone__query",
        "--output-format", "json"
    ]
    
    # Resume wenn Session existiert
    if issue_id in SESSION_MAP:
        cmd.extend(["--resume", SESSION_MAP[issue_id]])
    
    # 4. Ausfuehren
    result = subprocess.run(cmd, capture_output=True, text=True)
    output = json.loads(result.stdout)
    
    # 5. Session-ID speichern fuer naechstes Mal
    SESSION_MAP[issue_id] = output["session_id"]
    
    # 6. Ergebnis an GitHub posten
    post_github_comment(repo, issue_id, output["result"])

async def handle_ci_failure(data):
    run_id = data["check_run"]["id"]
    repo = data["repository"]["full_name"]
    
    cmd = [
        "claude", "-p",
        f"CI run {run_id} failed. Analyze the error and push a fix. "
        f"Query Pinecone for similar past failures.",
        "--continue",  # Letzte Session fortsetzen
        "--allowedTools", "Read,Edit,Bash,mcp__pinecone__query",
        "--output-format", "json"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    # ... Ergebnis verarbeiten
```

### 7.4 Was permanent laeuft vs. was on-demand laeuft

| Komponente | Laufzeit | Kosten |
|---|---|---|
| **FastAPI Server** | 24/7 | ~$5-20/Monat (Hetzner VPS) |
| **MCP Server (Pinecone)** | 24/7 | Minimal (leichtgewichtiger Prozess) |
| **Build-Cache** | Auf Disk | Einmalige Erstellung |
| **Claude Code Prozess** | On-Demand (Minuten pro Event) | API-Token-Kosten pro Aufruf |
| **Subagents** | On-Demand (innerhalb Claude) | Teil der Token-Kosten |

**Ergebnis: Die 24/7-Kosten sind minimal (~$5-20/Monat Server). Die eigentlichen Kosten entstehen nur wenn Claude arbeitet (Token-basiert).**

---

## 8. Empfehlung & Naechste Schritte

### Kurzfristige Empfehlung (MVP bis Mid-February)

1. **Webhook-Server aufsetzen** (FastAPI auf Hetzner VPS)
2. **Claude Code mit Subagents** (3 Agents: knowledge, coding, review)
3. **MCP Server fuer Pinecone** permanent auf dem Server
4. **Hook-System:**
   - `Stop` Hook: Review-Agent muss "ALL CLEAR" geben
   - `PreToolUse` Hook: Dangerous Commands blocken
   - `SessionStart` Hook: Automatisch Kontext laden
5. **Session-Resume** fuer State-Persistence zwischen Iterationen

### Mittelfristige Empfehlung

- Upgrade auf Agent Teams wenn Subagents limitieren
- Self-hosted Runner fuer lokale C++ Builds
- Build-Cache fuer Boost/Clang

### Langfristige Empfehlung

- Hybrid: Cursor CLI fuer schnelle Checks + Claude Code Agent Teams fuer komplexe Tasks
- AutoAgent GitHub Action fuer beide CLIs in einer Pipeline
- Graphiti oder aehnliches fuer langfristiges Projekt-Gedaechtnis (optional)

### Offene Fragen fuer Mid-February Meeting

1. Budget fuer Webhook-Server Infrastruktur (Hetzner vs AWS)?
2. Welcher Pinecone MCP Server wird genutzt (custom oder existing)?
3. Soll Cursor CLI parallel zu Claude Code evaluiert werden?
4. Wie wird der Build-Cache fuer Boost/Clang verwaltet (S3, lokal)?
5. Wie viele parallele Agents sollen laufen (Cost vs Speed)?
6. Agent Teams (experimental) vs Subagents (stabil) - welches Risiko-Level?
7. Manager-Pattern wie Atomic.Net oder einfacherer Ansatz?

---

**Quellen:**
- Huddle Transcript: Will Pak & SG, 3. Februar 2026
- [github.com/getzep/graphiti](https://github.com/getzep/graphiti)
- [docs.cursor.com/cli](https://docs.cursor.com/en/cli/overview)
- [code.claude.com/docs/en/hooks](https://code.claude.com/docs/en/hooks)
- [code.claude.com/docs/en/agent-teams](https://code.claude.com/docs/en/agent-teams)
- [code.claude.com/docs/en/headless](https://code.claude.com/docs/en/headless) (SDK/Programmatic Usage)
- [Atomic.Net Manager Agent](https://raw.githubusercontent.com/SteffenBlake/Atomic.Net/refs/heads/main/.github/agents/manager.agent.md)
- [cursor.com/cli](https://cursor.com/cli)
- [anthropics/claude-code-action](https://github.com/anthropics/claude-code-action)
- Diverse Web-Recherchen (Feb 2026)
