# Reference Repos — Deep Code Analysis

> **Zweck:** Konkrete Code-Patterns aus 6 Open-Source-Repos für unseren MVP.  
> **Erstellt:** 10. Feb 2026  
> **Repos geclont in:** `repos/`

---

## Inhaltsverzeichnis

1. [Direkt kopierbare Code-Patterns (Python/FastAPI)](#1-direkt-kopierbare-code-patterns)
2. [claude-hub — Webhook Pipeline](#2-claude-hub)
3. [observability — Dashboard + Event Schema](#3-observability)
4. [claude-code-fastapi — FastAPI Skeleton](#4-claude-code-fastapi)
5. [security-review — PR Review Prompts](#5-security-review)
6. [doppelganger — Duplicate Detection](#6-doppelganger)
7. [github-issues-analyzer — FastAPI + SQLite](#7-github-issues-analyzer)

---

## 1. Direkt kopierbare Code-Patterns

### 1.1 HMAC Webhook Signature Validation (→ FastAPI)

Aus claude-hub + doppelganger portiert nach Python:

```python
import hmac
import hashlib
from fastapi import Request, HTTPException

WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")

async def verify_github_signature(request: Request) -> bytes:
    """Validate GitHub webhook HMAC-SHA256 signature."""
    signature = request.headers.get("X-Hub-Signature-256")
    if not signature:
        raise HTTPException(status_code=401, detail="Missing signature")
    
    body = await request.body()
    calculated = "sha256=" + hmac.new(
        WEBHOOK_SECRET.encode("utf-8"), body, hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, calculated):  # Timing-safe!
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    return body
```

### 1.2 Authorized Users Allowlist (→ FastAPI)

Aus claude-hub:

```python
AUTHORIZED_USERS = [u.strip() for u in os.getenv("AUTHORIZED_USERS", "").split(",") if u.strip()]

async def check_authorized(sender_login: str, repo_name: str, issue_number: int):
    """Block unauthorized users from triggering agents."""
    if sender_login not in AUTHORIZED_USERS:
        # Post error comment to GitHub
        await github_post_comment(
            repo_name, issue_number,
            f"❌ Sorry @{sender_login}, only authorized users can trigger agent commands."
        )
        return False
    return True
```

### 1.3 Event-Schema für SQLite (→ Agent Dashboard)

Aus observability portiert:

```sql
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_app TEXT NOT NULL,
    session_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    agent_name TEXT,
    tool_name TEXT,
    payload TEXT NOT NULL,        -- JSON
    summary TEXT,
    timestamp INTEGER NOT NULL,
    cost_usd REAL
);

CREATE INDEX idx_session ON events(session_id);
CREATE INDEX idx_event_type ON events(event_type);
CREATE INDEX idx_timestamp ON events(timestamp);
```

### 1.4 WebSocket Broadcast (→ HTMX Dashboard)

Aus observability portiert nach FastAPI:

```python
from fastapi import WebSocket
from typing import Set

connected_clients: Set[WebSocket] = set()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        # Send recent events on connect
        recent = db.get_recent_events(limit=100)
        await websocket.send_json({"type": "initial", "data": recent})
        # Keep connection alive
        while True:
            await websocket.receive_text()
    except:
        connected_clients.discard(websocket)

async def broadcast_event(event: dict):
    """Send new event to all connected dashboard clients."""
    message = {"type": "event", "data": event}
    dead = set()
    for client in connected_clients:
        try:
            await client.send_json(message)
        except:
            dead.add(client)
    connected_clients -= dead
```

### 1.5 Claude Code Session Start + Resume (→ Agent Spawner)

Aus e2b-dev/claude-code-fastapi portiert:

```python
import subprocess
import json

session_map: dict[str, str] = {}  # session_id → working_dir

def run_claude_agent(prompt: str, session_id: str = None, 
                     allowed_tools: list = None, max_budget: float = 2.0) -> dict:
    """Spawn Claude Code agent with optional session resume."""
    cmd = ["claude", "-p", "--output-format", "json", 
           "--dangerously-skip-permissions"]
    
    if session_id and session_id in session_map:
        cmd.extend(["--resume", session_id])
    
    if allowed_tools:
        cmd.extend(["--allowedTools", ",".join(allowed_tools)])
    
    # Pipe prompt via stdin
    result = subprocess.run(
        cmd, input=prompt, capture_output=True, text=True, timeout=600
    )
    
    response = json.loads(result.stdout)
    
    # Store session for resume
    if "session_id" in response:
        session_map[response["session_id"]] = os.getcwd()
    
    return response
```

### 1.6 MCP Config (→ Pinecone Integration)

Aus e2b-dev portiert für unsere Pinecone MCP:

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

### 1.7 Robust JSON Parsing (→ Agent Output)

Aus anthropics/security-review — Claude gibt nicht immer sauberes JSON:

```python
import re
import json

def parse_claude_json(text: str) -> dict | None:
    """Extract JSON from Claude's output with multiple fallbacks."""
    # 1. Direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # 2. Extract from markdown code block
    for pattern in [r'```json\s*(.*?)\s*```', r'```\s*(\{.*?\})\s*```']:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                continue
    
    # 3. Find balanced braces
    depth = 0
    start = -1
    for i, c in enumerate(text):
        if c == '{':
            if depth == 0:
                start = i
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0 and start != -1:
                try:
                    return json.loads(text[start:i+1])
                except json.JSONDecodeError:
                    continue
    
    return None
```

### 1.8 False-Positive-Filter für Review Agent

Aus anthropics/security-review — Pattern-basiertes Filtering:

```python
import re

# Findings die wir für C++ Reviews NICHT reporten wollen
EXCLUDE_PATTERNS = [
    # DoS / Resource Exhaustion
    (r'\b(denial of service|dos attack|resource exhaustion)\b', "DoS finding"),
    (r'\b(exhaust|overwhelm).*?(resource|memory|cpu)\b', "Resource exhaustion"),
    # Rate Limiting
    (r'\b(missing|lack of|no)\s+rate\s+limit', "Rate limiting recommendation"),
    # Low-signal
    (r'\b(potential\s+memory\s+leak)\b', "Potential memory leak (speculative)"),
    (r'\b(open redirect|unvalidated redirect)\b', "Open redirect (low impact)"),
]

def should_exclude_finding(description: str, category: str = "") -> str | None:
    """Return exclusion reason or None if finding should be kept."""
    text = f"{category} {description}".lower()
    for pattern, reason in EXCLUDE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return reason
    return None
```

---

## 2. claude-hub

**Repo:** `repos/claude-hub/` | [GitHub](https://github.com/claude-did-this/claude-hub) | 344⭐

### Architektur

```
GitHub Webhook POST → Express Router → Signature Verify → Event Parse → Command Extract → Auth Check → Docker Container → Claude Code CLI → GitHub API Response
```

### Key Files

| File | Was drin ist |
|------|-------------|
| `src/providers/github/GitHubWebhookProvider.ts` | HMAC Signatur, Event Parsing, Event Normalization |
| `src/controllers/githubController.ts` | Command Extraction (`@Bot command`), Authorized Users Check, Bot Mention Handler |
| `src/services/claudeService.ts` | Docker Container Management, Claude Code Execution |
| `src/providers/claude/services/SessionManager.ts` | Session Lifecycle, Container Creation, Dependency Queuing |
| `.env.example` | Alle Env Vars mit Defaults |
| `scripts/runtime/claudecode-entrypoint.sh` | Container Entrypoint (Repo Clone, Git Setup, Claude Execution) |

### Env Vars (die wichtigsten für uns)

| Variable | Zweck | Unser Äquivalent |
|----------|-------|-------------------|
| `BOT_USERNAME` | GitHub Bot Account | `BOT_USERNAME` |
| `GITHUB_WEBHOOK_SECRET` | HMAC Secret | `GITHUB_WEBHOOK_SECRET` |
| `GITHUB_TOKEN` | Repo Access | `GITHUB_TOKEN` |
| `AUTHORIZED_USERS` | Comma-separated Allowlist | `AUTHORIZED_USERS` |
| `ANTHROPIC_API_KEY` | Claude API | `ANTHROPIC_API_KEY` |
| `CONTAINER_LIFETIME_MS` | Container Timeout (2h default) | `AGENT_TIMEOUT_SECONDS` |
| `REPO_CACHE_DIR` | Repo Cache Pfad | `REPO_CACHE_DIR` |
| `REPO_CACHE_MAX_AGE_MS` | Cache TTL (1h default) | `REPO_CACHE_TTL_SECONDS` |

### Event Types die claude-hub verarbeitet

| GitHub Event | Action | Was passiert |
|-------------|--------|-------------|
| `issues.opened` | Auto-Tagging | Label wird gesetzt |
| `issue_comment.created` | Bot Mention Check | Command wird extrahiert und ausgeführt |
| `pull_request.created` | Bot Mention Check | PR wird analysiert |
| `check_suite.completed` | Auto PR Review | Review wird getriggert |

### Command Extraction Pattern

```python
# Python-Port des TypeScript Regex:
import re

BOT_USERNAME = os.getenv("BOT_USERNAME", "ClaudeBot")
escaped = re.escape(BOT_USERNAME)
mention_regex = re.compile(rf"@?{escaped}\s+(.*)", re.DOTALL)

def extract_command(comment_body: str) -> str | None:
    match = mention_regex.search(comment_body)
    return match.group(1).strip() if match else None
```

### Session Management

- Sessions sind Docker Container mit Volume Mounts
- Session ID = Claude CLI Session ID
- Dependency Queuing: Sessions können voneinander abhängen
- In-Memory Map (kein DB Persistence) — für uns: SQLite

---

## 3. observability

**Repo:** `repos/claude-code-hooks-multi-agent-observability/` | [GitHub](https://github.com/disler/claude-code-hooks-multi-agent-observability) | 1038⭐

### Architektur

```
Claude Code Agent → Hook Script (Python) → HTTP POST → Bun Server → SQLite → WebSocket → Vue Dashboard
```

Für uns: `Claude Agent SDK → FastAPI Log Collector → SQLite → WebSocket → HTMX Dashboard`

### SQLite Schema (direkt übernehmbar)

```sql
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_app TEXT NOT NULL,          -- "knowledge-agent", "coding-agent", etc.
    session_id TEXT NOT NULL,          -- Agent Session ID
    hook_event_type TEXT NOT NULL,     -- "PreToolUse", "PostToolUse", etc.
    payload TEXT NOT NULL,             -- JSON: full event data
    chat TEXT,                         -- JSON: conversation transcript (optional)
    summary TEXT,                      -- AI-generated summary (optional)
    timestamp INTEGER NOT NULL,        -- Unix timestamp in ms
    model_name TEXT                    -- "sonnet", "opus", etc.
);

-- Performance indexes
CREATE INDEX idx_source_app ON events(source_app);
CREATE INDEX idx_session_id ON events(session_id);
CREATE INDEX idx_hook_event_type ON events(hook_event_type);
CREATE INDEX idx_timestamp ON events(timestamp);
```

### 12 Hook Event Types

| Event | Wann | Key Fields |
|-------|------|-----------|
| `SessionStart` | Agent startet | `source`, `agent_type`, `model` |
| `SessionEnd` | Agent endet | `reason` |
| `UserPromptSubmit` | Prompt gesendet | Full prompt |
| `PreToolUse` | VOR Tool-Aufruf (kann blocken!) | `tool_name`, `tool_input` |
| `PostToolUse` | NACH Tool-Aufruf | `tool_name`, `tool_response` |
| `PostToolUseFailure` | Tool Fehler | `tool_name`, `error`, `is_interrupt` |
| `PermissionRequest` | Permission Dialog | `tool_name`, `permission_suggestions` |
| `Notification` | Claude Notification | `notification_type` |
| `SubagentStart` | Subagent spawnt | `agent_id`, `agent_type` |
| `SubagentStop` | Subagent fertig | `agent_id`, `agent_transcript_path` |
| `Stop` | Claude stoppt | `stop_hook_active` |
| `PreCompact` | Context Compaction | `custom_instructions` |

### Agent Team Definitionen

**Builder Agent** (= unser Coding Agent):
```markdown
name: builder
model: opus
Capabilities: Read, Edit, Write, Bash, Git — ALLES
PostToolUse Hooks: ruff + type checker nach jedem Write/Edit
```

**Validator Agent** (= unser Review Agent):
```markdown
name: validator
model: opus
disallowedTools: Write, Edit, NotebookEdit
Capabilities: Read-only + Bash für Tests
```

### WebSocket Message Types

```json
// Bei Verbindung: alle letzten Events
{ "type": "initial", "data": [event1, event2, ...] }

// Bei neuem Event: Broadcast an alle Clients
{ "type": "event", "data": { "id": 42, "source_app": "...", ... } }
```

---

## 4. claude-code-fastapi

**Repo:** `repos/claude-code-fastapi/` | [GitHub](https://github.com/e2b-dev/claude-code-fastapi) | 17⭐

### Endpoints

```python
# Neuer Chat starten
POST /chat
Body: { "prompt": "...", "repo": "https://github.com/owner/repo" }

# Session fortsetzen
POST /chat/{session_id}
Body: { "prompt": "..." }
```

### Response Format (von Claude Code CLI)

```json
{
    "type": "result",
    "subtype": "success",
    "is_error": false,
    "duration_ms": 216401,
    "session_id": "038b769b-4717-47ca-be02-2a49bd7da978",
    "result": "...",
    "total_cost_usd": 1.14,
    "usage": {
        "input_tokens": 300,
        "cache_creation_input_tokens": 77458,
        "cache_read_input_tokens": 2087724,
        "output_tokens": 13935
    }
}
```

### Claude Code Invocation

```bash
echo '{prompt}' | claude -p --dangerously-skip-permissions --output-format json --mcp-config /.mcp/mcp.json --resume {session_id}
```

### Dependencies (minimal)

```
fastapi[standard]>=0.116.1
dotenv>=0.9.9
```

---

## 5. security-review

**Repo:** `repos/claude-code-security-review/` | [GitHub](https://github.com/anthropics/claude-code-security-review) | 2967⭐

### Prompt Template (GOLD für unseren Review Agent)

Der Security-Prompt ist ~4000 Zeichen. Die Struktur:

```
1. ROLLE: "You are a senior security engineer..."
2. CONTEXT: Repository, Author, Files changed, Lines added/deleted
3. DIFF: Full unified diff (oder Fallback: "use file exploration tools")
4. OBJECTIVE: "Perform a security-focused code review..."
5. CRITICAL INSTRUCTIONS: Minimize false positives, >80% confidence
6. SECURITY CATEGORIES: 6 Kategorien mit je 3-6 Subcategories
7. METHODOLOGY: 3 Phasen (Context → Comparative → Vulnerability)
8. OUTPUT FORMAT: Strict JSON schema mit findings[]
9. SEVERITY GUIDELINES: HIGH/MEDIUM/LOW Definitionen
10. CONFIDENCE SCORING: 0.7-1.0 Range mit Beschreibungen
11. EXCLUSIONS: Was NICHT reporten (DoS, rate limiting, etc.)
```

**Für unseren C++ Review Agent adaptieren:**
- Rolle ändern: "senior C++ compiler engineer" statt "security engineer"
- Categories ändern: C++ best practices, LLVM coding standards, memory safety
- Methodology: Phase 1 = Pinecone MCP Query (Richard Smith Patterns)
- Output Format: beibehalten (JSON mit findings[])

### False-Positive-Filtering Kategorien

| Kategorie | Patterns | Aktion |
|-----------|----------|--------|
| DoS | `denial of service`, `resource exhaustion` | Exclude |
| Rate Limiting | `missing rate limit`, `unlimited requests` | Exclude |
| Resource Leaks | `potential memory leak`, `unclosed connection` | Exclude |
| Open Redirect | `open redirect`, `unvalidated redirect` | Exclude |
| Regex Injection | `regex injection`, `regex dos` | Exclude |
| Memory Safety (non-C++) | `buffer overflow` in .py/.js files | Exclude |
| SSRF in HTML | `ssrf` in .html files | Exclude |
| Markdown Files | Any finding in .md files | Exclude |

### Diff Analysis

```python
# PR Diff holen (unified format)
url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
headers["Accept"] = "application/vnd.github.diff"
diff = requests.get(url, headers=headers).text

# Generated Files filtern
if "@generated by" in section:
    continue  # Skip auto-generated code
```

### JSON Parsing (3-Stufen Fallback)

1. `json.loads(text)` — direkt
2. Markdown Code Block extrahieren — `\`\`\`json ... \`\`\``
3. Balanced Braces finden — `{` zählen bis `}` matched

---

## 6. doppelganger

**Repo:** `repos/doppelganger/` | [GitHub](https://github.com/dannyl1u/doppelganger) | 22⭐

### Duplicate Detection Logik

```python
# 1. Embedding generieren
model = SentenceTransformer("all-MiniLM-L6-v2")
full_issue = f"{issue_title} {issue_body}"
embedding = model.encode(full_issue).tolist()

# 2. Similarity Query (ChromaDB)
results = collection.query(query_embeddings=[embedding], n_results=1)
distance = results["distances"][0][0]  # Cosine distance (0=identical, 2=opposite)

# 3. Entscheidung
THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD"))  # z.B. 0.8

if distance < 1 - THRESHOLD:          # Sehr ähnlich → SCHLIESSEN
    close_issue() + comment("Duplicate of #X")
elif distance < 1 - (THRESHOLD * 0.5): # Mittlere Ähnlichkeit → KOMMENTIEREN
    comment("Possibly related to #X")
else:                                   # Niedrig → Trotzdem kommentieren
    comment("Most similar: #X")

# 4. Immer speichern (für zukünftige Vergleiche)
collection.add(documents=[full_issue], embeddings=[embedding], ...)
```

### ChromaDB Collection Pattern

```python
# Eine Collection pro Repository
collection_name = f"github_issues_{repo_id}"
collection = chroma_client.get_or_create_collection(collection_name)

# Speichern
collection.add(
    documents=[full_issue],
    metadatas=[{"issue_number": str(num), "title": title}],
    embeddings=[embedding],
    ids=[f"{repo_id}_{issue_number}"]
)
```

**Für uns:** Pinecone statt ChromaDB, aber das Threshold-Pattern ist 1:1 übernehmbar.

---

## 7. github-issues-analyzer

**Repo:** `repos/github-issues-analyzer/` | [GitHub](https://github.com/sharjeelyunus/github-issues-analyzer) | 1⭐

### FastAPI + SQLite Pattern

```python
# Endpoints
GET /issues              → Alle Issues mit Metadata
GET /issues/{github_id}  → Einzelnes Issue mit Duplicates
GET /duplicates          → Nur Issues mit Duplicates
GET /labels              → Issues mit Labels
GET /priorities-severities → Priority/Severity Predictions
```

### SQLite Schema

```sql
CREATE TABLE issues (
    id INTEGER PRIMARY KEY,
    github_id INTEGER UNIQUE,
    title TEXT,
    body TEXT,
    embedding BLOB,       -- Pickle-serialized numpy array
    duplicates TEXT,       -- Stringified list
    labels TEXT,           -- JSON string
    priority TEXT,         -- "low" | "medium" | "high"
    severity TEXT          -- "minor" | "major" | "critical"
);
```

### Similarity: O(n²) Pairwise vs Vector DB

Dieses Repo vergleicht ALLE Paare (langsam bei 7k Issues):
```python
for issue_a in issues:
    for issue_b in issues:
        similarity = cos_sim(embedding_a, embedding_b)
        if similarity >= 0.8:
            duplicates.append(...)
```

**Für uns:** Pinecone MCP macht das in Millisekunden per Vector Search. Kein O(n²) nötig.

---

## Zusammenfassung: Was wir von wo übernehmen

| Unser Kapitel | Was | Von welchem Repo | Konkretes File |
|---------------|-----|-----------------|----------------|
| **Kap 2: FastAPI** | HMAC Signature Validation | claude-hub + doppelganger | `GitHubWebhookProvider.ts` / `webhook_handler.py` |
| **Kap 2: FastAPI** | Authorized Users Allowlist | claude-hub | `githubController.ts:438-479` |
| **Kap 2: FastAPI** | Command Extraction Regex | claude-hub | `githubController.ts` |
| **Kap 2: FastAPI** | Event Routing Pattern | claude-hub | `WebhookProcessor.ts` |
| **Kap 3: Agents** | Claude Code Session Resume | claude-code-fastapi | `app/main.py` |
| **Kap 3: Agents** | Agent Tool Restrictions | observability | `.claude/agents/team/validator.md` |
| **Kap 3: Agents** | JSON Output Parsing | security-review | `json_parser.py` |
| **Kap 3: Agents** | False-Positive Filtering | security-review | `findings_filter.py` |
| **Kap 4: Dashboard** | SQLite Event Schema | observability | `db.ts` |
| **Kap 4: Dashboard** | WebSocket Broadcast | observability | `index.ts` |
| **Kap 4: Dashboard** | 12 Event Types | observability | `settings.json` |
| **Kap 5: MCP** | MCP JSON Config | claude-code-fastapi | `template/.mcp.json` |
| **Kap 5: MCP** | Similarity Threshold | doppelganger | `config.py` |
| **Review Agent** | Prompt Template Structure | security-review | `prompts.py` |
| **Review Agent** | 3-Phase Methodology | security-review | `prompts.py` |
| **Review Agent** | Diff Analysis | security-review | `github_action_audit.py` |
