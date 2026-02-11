# SG's Execution Blueprint — C++ Alliance Agent

**Ziel:** AI Agent der PRs reviewed wie Richard Smith.  
**Client:** Vinnie Falco + Will Pak (C++ Alliance)  
**Deadline:** ~16. Feb 2026 (Live Demo für Will)  
**Infra:** Azure VM ($5000 MS Credits)  
**Stack:** FastAPI (Webhook) + Claude Code CLI (Built-in Subagents) + HTMX Dashboard  
**Research:** ✅ ABGESCHLOSSEN (10. Feb 2026)

---

## Architektur (NEU — mit Built-in Orchestration)

```
GitHub Event (Issue/PR/CI)
    │
    ▼
┌──────────────────────────────────────────────────┐
│           FastAPI Server (unser Code)             │
│                                                   │
│  POST /webhook → HMAC Check → Auth Check          │
│       → Event Routing → subprocess("claude")      │
│       → SQLite Logging → WebSocket Broadcast      │
│                                                   │
│  GET  /dashboard → HTMX + Jinja2 Templates        │
│  WS   /ws       → Live Agent Status               │
└──────────────────────┬───────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────┐
│      Claude Code CLI (Built-in Orchestration)     │
│                                                   │
│  claude --agent orchestrator -p "..." \            │
│    --output-format json                           │
│                                                   │
│  Claude liest .claude/agents/ und delegiert:       │
│                                                   │
│  ┌─────────────┐ ┌─────────────┐ ┌────────────┐  │
│  │ knowledge   │ │ coding      │ │ review     │  │
│  │ agent       │ │ agent       │ │ agent      │  │
│  │             │ │             │ │            │  │
│  │ model:haiku │ │ model:opus  │ │model:sonnet│  │
│  │ MCP:pinecone│ │ all tools   │ │ read-only  │  │
│  │ read-only   │ │             │ │ + bash     │  │
│  └─────────────┘ └─────────────┘ └────────────┘  │
│                                                   │
│  + Session Resume (--resume)                      │
│  + Prompt Caching (90% Ersparnis)                 │
│  + .claudeignore + CLAUDE.md                      │
└──────────────────────────────────────────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │   Pinecone MCP  │
              │  (Will's Package)│
              └─────────────────┘
```

**Was WIR bauen:** FastAPI Server (~300 Zeilen) + Dashboard (~200 Zeilen) + 4 Agent-Definitionen (Markdown)  
**Was CLAUDE macht:** Subagent Spawning, Model Selection, Tool Routing, Context Isolation, Pipeline

---

## AUSFÜHRUNGS-FAHRPLAN

### Kapitel 1: Infrastruktur (Tag 1 — ~3h)

**1.1 Azure VM aufsetzen**
```bash
# Azure Portal → Create VM
# Image: Ubuntu 22.04 LTS
# Size: B2ms (2 vCPU, 8 GB RAM, ~$60/Mo)
# Auth: SSH Key
# Networking: Port 80, 443, 22 offen
```
- [ ] MS Startup Credits aktivieren ($5000)
- [ ] VM erstellen + SSH Key
- [ ] SSH verbinden: `ssh azureuser@<IP>`
- [ ] System updaten: `sudo apt update && sudo apt upgrade -y`
- [ ] Python 3.11+ installieren: `sudo apt install python3.11 python3.11-venv python3-pip -y`
- [ ] Node.js installieren (für MCP): `curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - && sudo apt install nodejs -y`
- [ ] nginx installieren: `sudo apt install nginx certbot python3-certbot-nginx -y`
- [ ] Claude Code installieren: `npm install -g @anthropic-ai/claude-code`
- [ ] Claude Code authentifizieren: `claude login`

**1.2 Test-Repo auf GitHub**
- [ ] Neues Repo erstellen: `cppalliance-agent-demo`
- [ ] Webhook konfigurieren:
  - Payload URL: `https://<DOMAIN>/webhook`
  - Content Type: `application/json`
  - Secret: generieren und in `.env` speichern
  - Events: "Send me everything"
- [ ] Webhook Secret in `.env` auf VM speichern

**1.3 Domain + SSL**
```bash
# nginx Config
sudo nano /etc/nginx/sites-available/agent
# → proxy_pass http://localhost:8000;
sudo ln -s /etc/nginx/sites-available/agent /etc/nginx/sites-enabled/
sudo certbot --nginx -d agent.example.com
```

---

### Kapitel 2: FastAPI Server (Tag 1-2 — ~4h)

**2.1 Projekt-Struktur erstellen**
```
cppalliance-agent/
├── .env                          ← Secrets (NICHT committen!)
├── .gitignore
├── .claudeignore
├── CLAUDE.md                     ← Projekt-Kontext für Claude (<500 Zeilen)
├── .claude/
│   └── agents/
│       ├── orchestrator.md       ← Haupt-Agent (delegiert an Subagents)
│       ├── knowledge-agent.md    ← Haiku, MCP, read-only
│       ├── coding-agent.md       ← Opus, full access
│       └── review-agent.md       ← Sonnet, read + bash
├── app/
│   ├── main.py                   ← FastAPI Server (~150 Zeilen)
│   ├── webhook.py                ← HMAC + Auth + Event Routing (~80 Zeilen)
│   ├── agent_runner.py           ← subprocess("claude --agent ...") (~50 Zeilen)
│   ├── database.py               ← SQLite Schema + Queries (~40 Zeilen)
│   └── websocket.py              ← Dashboard WebSocket (~30 Zeilen)
├── templates/
│   └── dashboard.html            ← HTMX + TailwindCSS (~200 Zeilen)
├── requirements.txt
└── systemd/
    └── agent.service             ← systemd Unit File
```

**2.2 `.env` Datei**
```env
GITHUB_WEBHOOK_SECRET=<generiertes-secret>
GITHUB_TOKEN=<github-pat>
BOT_USERNAME=cppalliance-bot
AUTHORIZED_USERS=vinniefalco,willpak,sabriguenes
ANTHROPIC_API_KEY=<dein-key>
PINECONE_API_KEY=<wills-key>
REPO_CACHE_DIR=/var/cache/agent-repos
```

**2.3 FastAPI Grundgerüst**  
- [ ] `pip install fastapi uvicorn aiosqlite httpx`
- [ ] `POST /webhook` → HMAC Signature Check (aus `REFERENCE-REPOS-ANALYSIS.md` Pattern 1.1)
- [ ] Authorized Users Check (Pattern 1.2)
- [ ] Event Routing:
  - `issue_comment.created` + Bot Mention → Pipeline starten
  - `pull_request.opened` → Review Agent direkt
  - `check_run.completed` + failure → CI-Fixer
- [ ] Command Extraction: `@BotName <command>` → command extrahieren
- [ ] SQLite: Events-Tabelle (Pattern 1.3 aus REFERENCE-REPOS-ANALYSIS.md)
- [ ] WebSocket `/ws` für Dashboard (Pattern 1.4)

---

### Kapitel 3: Agent-Definitionen (Tag 2 — ~2h)

**Das ist der Kern.** Keine Python-Klassen mehr — nur Markdown-Dateien.

**3.1 `.claude/agents/orchestrator.md`**
```markdown
---
name: orchestrator
description: Orchestrates C++ code review pipeline. Use for every GitHub event.
model: sonnet
tools: Task(knowledge-agent, coding-agent, review-agent), Read, Grep, Glob
permissionMode: bypassPermissions
---
You are the C++ Alliance Code Review Orchestrator.

PIPELINE:
1. Delegate to knowledge-agent: Get relevant C++/Clang review patterns from Pinecone
2. Based on context, decide: Does this need code changes?
   - YES → Delegate to coding-agent with knowledge context
   - NO → Summarize findings and respond
3. After coding-agent: Delegate to review-agent to validate changes
4. If review-agent says "NEEDS FIXES" → Send back to coding-agent (max 3 loops)
5. If review-agent says "ALL CLEAR" → Report success

RULES:
- NEVER write code yourself. ONLY delegate.
- ALWAYS start with knowledge-agent for context.
- Include cost tracking in your summary.
```

**3.2 `.claude/agents/knowledge-agent.md`**
```markdown
---
name: knowledge-agent
description: Queries Pinecone for C++/Clang review knowledge. Use proactively.
model: haiku
tools: Read, Grep, Glob
mcpServers:
  - pinecone-search
permissionMode: plan
---
You are a Knowledge Agent for the C++ Alliance.
Query the Pinecone MCP for relevant C++ review patterns, compiler knowledge,
and Richard Smith's review style. Return a concise context summary.
Focus on: What patterns apply? What would an expert reviewer flag?
```

**3.3 `.claude/agents/coding-agent.md`**
```markdown
---
name: coding-agent
description: Implements code changes and fixes for C++ projects
model: opus
permissionMode: bypassPermissions
---
You are a Coding Agent. Implement the requested changes based on the
knowledge context provided. Follow C++ best practices and LLVM coding standards.
Create clean commits with descriptive messages.
```

**3.4 `.claude/agents/review-agent.md`**
```markdown
---
name: review-agent
description: Reviews code changes for C++ quality and best practices
model: sonnet
tools: Read, Grep, Glob, Bash
disallowedTools: Write, Edit
permissionMode: plan
---
You are a Code Review Agent. Review the changes made by the coding agent.
Check for: correctness, C++ best practices, LLVM coding standards,
potential bugs, performance issues.

Output EXACTLY one of:
- "ALL CLEAR" + summary of what was reviewed
- "NEEDS FIXES" + specific list of issues to fix
```

**3.5 MCP Config: `.claude/mcp.json`** (im Projekt-Root)
```json
{
  "mcpServers": {
    "pinecone-search": {
      "command": "npx",
      "args": ["-y", "@will-cppa/pinecone-read-only-mcp"],
      "env": {
        "PINECONE_API_KEY": "${PINECONE_API_KEY}"
      }
    }
  }
}
```

---

### Kapitel 4: Agent Runner (Tag 2-3 — ~2h)

**4.1 `app/agent_runner.py`** — Der einzige Glue-Code
```python
import subprocess, json, os

REPO_CACHE = os.getenv("REPO_CACHE_DIR", "/var/cache/agent-repos")

async def run_agent(prompt: str, repo_name: str, session_id: str = None) -> dict:
    """Startet Claude mit Built-in Orchestration."""
    # Repo cachen
    repo_dir = clone_or_update(repo_name)
    
    cmd = [
        "claude", "--agent", "orchestrator",
        "-p", "--output-format", "json",
        "--dangerously-skip-permissions",
    ]
    if session_id:
        cmd.extend(["--resume", session_id])
    
    result = subprocess.run(
        cmd, input=prompt, capture_output=True, text=True,
        cwd=repo_dir, timeout=600,
        env={**os.environ, "PINECONE_API_KEY": os.getenv("PINECONE_API_KEY")}
    )
    
    return parse_claude_json(result.stdout)  # Pattern 1.7 aus REFERENCE-REPOS-ANALYSIS.md
```

Das ist der **gesamte Agent-Spawning Code.** Claude Code handelt den Rest.

---

### Kapitel 5: Dashboard (Tag 3-4 — ~3h)

- [ ] HTMX + TailwindCSS + Jinja2 Template
- [ ] Event-Schema aus `REFERENCE-REPOS-ANALYSIS.md` Pattern 1.3
- [ ] WebSocket Broadcast aus Pattern 1.4
- [ ] Panels: Active Agents | Live Logs | Token Costs | System Health

---

### Kapitel 6: MCP Integration (Tag 4 — ~1h)

- [x] ~~Will anschreiben~~ — ✅ MCP Zugang erhalten!
- [ ] MCP lokal testen: `npx -y @will-cppa/pinecone-read-only-mcp` → funktioniert?
- [ ] MCP auf Azure VM deployen (Node.js ist schon installiert von Kap. 1)
- [ ] Knowledge Agent mit MCP verbinden (ist schon in der Agent-Definition drin)
- [ ] Test-Query: "What are common review patterns for template metaprogramming?"

---

### Kapitel 7: End-to-End Test (Tag 5 — ~3h)

- [ ] Issue im Test-Repo erstellen → Webhook feuert → Agent reagiert automatisch
- [ ] PR erstellen → Review Agent postet Kommentar auf GitHub
- [ ] CI Failure simulieren → CI-Fixer Agent reagiert
- [ ] Dashboard zeigt alles live (Events, Logs, Kosten)
- [ ] Session Resume testen (`--resume`)
- [ ] Edge Cases: Unauthorized User, Malformed Webhook, Timeout

---

### Kapitel 8: Demo vorbereiten (Tag 6 — ~2h)

- [ ] Live Demo 3x komplett durchspielen
- [ ] Talking Points:
  - "This is a working prototype on our Azure VM"
  - "Webhook → Agent response in seconds, not hours"
  - "Full observability through the dashboard"
  - "Knowledge layer via your Pinecone MCP — already connected"
  - "Phase 2: your team takes this to production"
- [ ] Kosten-Kalkulation finalisieren für Meeting
- [ ] Fallback: Falls irgendwas nicht klappt → Screen Recording als Backup

---

## Abhängigkeiten

| Was | Status | Details |
|-----|--------|---------|
| MCP Server Package | ✅ Erhalten | `npx -y @will-cppa/pinecone-read-only-mcp` |
| Pinecone API Key | ✅ Erhalten | In `.env` (NICHT committen!) |
| Anthropic API Key | ✅ Hab ich | — |
| Azure Credits | ✅ $5000 | 76 Monate Runway |
| GitHub Test-Repo | ✅ Kann ich | — |
| Claude Code CLI | ✅ Verfügbar | `npm install -g @anthropic-ai/claude-code` |

**Alle Abhängigkeiten gelöst. Nichts blockiert den Start.**

---

## Kosten-Spickzettel

| Was | Kosten | Wer zahlt |
|-----|--------|-----------|
| Azure VM | ~$60/Monat | MS Credits |
| Knowledge Agent (Haiku) | ~$0.01-0.05/call | API Key |
| Review Agent (Sonnet) | ~$0.10-0.30/call | API Key |
| Coding Agent (Opus) | ~$0.50-2.00/call | API Key |
| Prompt Caching | -90% auf wiederkehrende Tokens | Automatisch |

**Kosten-Optimierung:** Haiku für häufige Calls, Opus nur wenn gecodet wird, Prompt Caching, `.claudeignore`, `MAX_THINKING_TOKENS=8000` für einfache Tasks.

---

## Wichtige Entscheidungen

1. **Warum Built-in Subagents statt custom SDK?** → Claude Code hat native Orchestration seit Opus 4.6. Markdown-Dateien statt Python-Klassen. Halbiert unseren Code.
2. **Warum Subagents, nicht Agent Teams?** → Pipeline ist sequentiell, 7x weniger Tokens. Upgrade-Pfad bleibt.
3. **Warum FastAPI trotzdem?** → Webhook Reception + Dashboard + Logging. Claude Code kann keine Webhooks empfangen.
4. **Warum Azure?** → $5000 Credits. Opus 4.6 auch auf Azure Foundry verfügbar (Phase 2).
5. **Warum 3-Tier Model Selection?** → Haiku (häufig+billig) → Sonnet (mittel) → Opus (selten+teuer). 81%+ Ersparnis.

---

## Reference-Dokumente

| Datei | Inhalt |
|-------|--------|
| `REFERENCE-REPOS-ANALYSIS.md` | Deep Analysis 7 Repos + 8 kopierbare Code-Patterns |
| `CONSULTANT-PAPER-AGENT-ARCHITECTURE.md` | Client-facing Proposal (Englisch) |
| `QA-ARCHITECTURE-DECISIONS.md` | 6 Architektur-Fragen beantwortet |
| `PROPOSAL-FIDELITY-ARCHITECTURE-THEAUDITOR.md` | Database-First Pattern |
| `RESEARCH-CLI-HOOKS-ARCHITECTURE-DE.md` | CLI Vergleich (Deutsch) |
| `PROJECT-PLAN.md` | Vollständiger Plan mit Kontext + History |

**Open-Source Referenzen:** 7 Repos geclont in `repos/` — siehe Abschnitt in `REFERENCE-REPOS-ANALYSIS.md` für Details.

---

## Research Status: ✅ ABGESCHLOSSEN

Alles was researcht werden musste ist researcht. Die nächste Aktion ist **Ausführung, nicht Research.**

**Starte mit Kapitel 1.1** → Azure VM aufsetzen.
