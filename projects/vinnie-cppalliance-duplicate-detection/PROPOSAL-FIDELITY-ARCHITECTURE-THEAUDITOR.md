# Proposal: Database-First Fidelity Architecture for LLVM/Clang Code Intelligence

**Type:** Architecture Proposal for Follow-Up Meeting  
**Date:** February 10, 2026  
**Author:** SG  
**Status:** DRAFT — Zur Diskussion im nächsten Meeting mit Will Pak  

---

## TL;DR

Wir haben ein existierendes Open-Source-Tool analysiert (**TheAuditor**, v2.0.4rc1, [GitHub](https://github.com/TheAuditorTool/Auditor)), das eine **Database-First Static Analysis** Architektur mit eingebautem **Fidelity-Verification-System** implementiert. Die Architektur-Patterns sind direkt anwendbar auf unser LLVM/Clang Code Review Agent Projekt. Dieses Dokument beschreibt die Learnings und einen konkreten Vorschlag für die Adaption auf C++.

> **Wichtig:** TheAuditor ist ab v3 closed source. Der Entwickler wurde zweimal während Due Diligence "gesherlocked" und hat zu einem Freemium-Produktmodell pivotiert. Wir respektieren das. Dieses Dokument bezieht sich ausschließlich auf die **öffentlich verfügbare v2.0.4rc1** (AGPL-3.0) und auf **Architektur-Konzepte**, nicht auf proprietären Code.

---

## 1. Hintergrund: Was ist TheAuditor?

### Überblick

| Eigenschaft | Detail |
|-------------|--------|
| **Name** | TheAuditor |
| **Beschreibung** | Database-First Static Analysis and Code Context Intelligence |
| **Core-Sprache** | Python |
| **Unterstützte Sprachen** | Python (native `ast`), JS/TS (TypeScript Compiler API), Go, Rust, Bash (tree-sitter) |
| **C++ Support** | ❌ Nicht vorhanden |
| **Lizenz (v2)** | AGPL-3.0 |
| **Status** | v2 archived (OSS), v3 closed source (Produkt-Pivot) |
| **GitHub** | [TheAuditorTool/Auditor](https://github.com/TheAuditorTool/Auditor) — 532 Stars, 54 Forks |

### Kernidee

Statt bei jeder Analyse Dateien neu zu parsen (wie traditionelle SAST-Tools), indexiert TheAuditor den gesamten Codebase **einmalig** in SQLite-Datenbanken und beantwortet danach alle Queries in < 1 Sekunde aus dem Index.

```
Traditionell:            TheAuditor:
Query → Parse → Analyse  Query → SQLite Lookup → Ergebnis (<1s)
       (langsam, N+1)            (vorberechnet, instant)
```

### Scale-Beweis (Fidelity Check vom 10. Feb 2026)

| Level | Geprüft | Accuracy | Ergebnis |
|-------|---------|----------|----------|
| **Level 1** (Syntaktisch) | 834.041 Code-Elemente | 18/18 OK, 1 FAIL (taint_sources 97.61%) | ~100% |
| **Level 2** (Semantisch) | ~128.797 Elemente | 1 OK, 3 FAIL (cfg_blocks 89.99%, cfg_types 96.19%, function_returns 94.32%) | 89-100% |

Das Volumen (834k Elemente) zeigt, dass strukturierte Code-Analyse im großen Maßstab mit dieser Architektur funktioniert.

---

## 2. Die Architektur-Patterns (Learnings)

### 2.1 Database-First Architecture

**Konzept:** Alles wird in SQLite indexiert, bevor irgendeine Analyse stattfindet.

| Datenbank | Inhalt | Typische Größe |
|-----------|--------|----------------|
| `repo_index.db` | Raw AST Facts: Symbole, Funktionsaufrufe, Imports, Assignments | 50-500+ MB |
| `graphs.db` | Pre-computed Graphs: Call Graph, Dependency Graph | 30-300+ MB |

**Warum relevant für uns:** Unser Knowledge-Agent braucht instant Zugriff auf Code-Strukturen aus dem LLVM-Repo. SQLite-Indexierung statt wiederholtem GitHub-API-Scraping / File-Parsing wäre ein massiver Performance-Gewinn.

### 2.2 Manifest-Receipt Reconciliation (Fidelity System)

**Das brillanteste Pattern.** An jeder Pipeline-Grenze wird Datenintegrität garantiert:

```
MANIFEST (vorher)          RECEIPT (nachher)         RECONCILE (vergleich)
─────────────────          ─────────────────         ────────────────────
"Ich werde gleich           "Ich habe tatsächlich     "Stimmt das überein?
 150 Symbole schreiben,      142 Symbole geschrieben,  8 gefiltert wegen
 tx_id abc123"               8 gefiltert für            FK_VIOLATION — OK.
                              FK_VIOLATION,             Delta vollständig
                              tx_id abc123"             erklärt."
```

**6-Stufen Fidelity Pipeline:**

| Stufe | Was passiert | Gate |
|-------|-------------|------|
| 1 | Raw Source Code → Datenbank: 1:1 lossless Überprüfung | GATE 1: Extraction Manifest |
| 2 | AST Extraction (pro Sprache) → Manifest mit tx_id, count, columns, bytes, hash | FidelityToken.attach_manifest() |
| 3 | Storage in DB → Receipt mit actual_writes, filtered_count, filter_reasons | FidelityToken.create_receipt() |
| 4 | Graph Building → Cross-referencing, Node ID Fidelity | node_id_fidelity, cross_lang_fid |
| 5 | Rule Execution → Ergebnisse gegen Index verifiziert | fidelity.py |
| 6 | Taint Analysis → Runtime-Transformation-Korrelation ("Engine Magic") | fidelity.py |

**Warum relevant für uns:** Wenn wir 100k+ PR-Kommentare aus LLVM scrapen und in eine Knowledge Base laden, **müssen** wir garantieren, dass nichts verloren geht. Ein Manifest-Receipt-System würde sicherstellen: "Wir haben 7.342 PRs mit 45.891 Review-Kommentaren gescraped → 45.891 Kommentare sind im Vector Store → 0 Verlust."

### 2.3 4-Layer Architecture

TheAuditor trennt Analyse in vier unabhängige Layer, jeder mit eigenen Fidelity-Checks:

```
┌─────────────────────────────────────────────────────────────┐
│              PIPELINE ORCHESTRATOR                            │
│              (aud full --offline / aud graph build)           │
├──────────────┬──────────────┬──────────────┬────────────────┤
│ INDEXER      │ GRAPH        │ RULES        │ TAINT          │
│ LAYER        │ LAYER        │ LAYER        │ LAYER          │
│ (Extraction) │ (Building)   │ (Execution)  │ (Analysis)     │
│              │              │              │                │
│ fidelity.py  │ fidelity.py  │ fidelity.py  │ fidelity.py    │
│ fidelity_    │ node_id_     │              │                │
│ utils        │ fidelity     │              │                │
│ roundtrip_   │ cross_lang_  │              │                │
│ fid.         │ fid.         │              │                │
└──────────────┴──────────────┴──────────────┴────────────────┘
```

**Warum relevant für uns:** Unsere Agent-Pipeline (Knowledge → Coding → Review) könnte ein analoges Layer-System nutzen:

| TheAuditor Layer | Unser Äquivalent |
|-----------------|-----------------|
| INDEXER (Extraction) | Data Scraper (GitHub API → SQLite) |
| GRAPH (Building) | Knowledge Graph (PR-Kommentare → Expertise Map → Vector DB) |
| RULES (Execution) | Agent Routing (Event → richtiger Agent) |
| TAINT (Analysis) | Code Review Agent (Datenfluss-Analyse in PRs) |

### 2.4 In-Language Extraction

**Entscheidender Design-Entscheid:** TheAuditor nutzt NICHT nur tree-sitter. Für Sprachen mit tiefer semantischer Analyse werden **native Compiler-APIs** verwendet:

| Sprache | Parser | Tiefe |
|---------|--------|-------|
| Python | Native `ast` Modul + 27 Extraktoren | Full Semantic |
| JS/TS | TypeScript Compiler API (via Node.js subprocess) | Full Semantic |
| Go, Rust, Bash | tree-sitter | Structural + Taint |

**Warum relevant für uns:** Für C++ bedeutet das: **`libclang` / Clang AST** ist das richtige Äquivalent — nicht tree-sitter. Clang's eigener AST versteht Templates, SFINAE, ADL, Overload Resolution — alles was tree-sitter's C++ Grammar nicht korrekt abbilden kann.

### 2.5 Four-Vector Convergence Engine (FCE)

Identifiziert High-Risk Code durch Konvergenz von 4 unabhängigen Analyse-Vektoren:

| Vektor | Signal | Quelle |
|--------|--------|--------|
| STATIC | Code Quality Issues | Linter-Ergebnisse |
| STRUCTURAL | Cyclomatic Complexity | CFG-Analyse |
| PROCESS | Frequently Modified Code | Git Churn |
| FLOW | Data Flow Vulnerabilities | Taint Propagation |

**Key Insight:** Wenn 3+ unabhängige Vektoren auf dieselbe Datei zeigen, ist die Confidence exponentiell höher als bei jedem einzelnen Tool.

**Warum relevant für uns:** Für unseren PR-Review-Agent könnten wir analoge Vektoren definieren:

| Vektor | Signal für PR Review |
|--------|---------------------|
| HISTORY | Wie oft wurde dieser Code-Bereich schon reviewed/revised? |
| EXPERTISE | Welche Experten haben diesen Bereich bisher reviewed? |
| COMPLEXITY | Wie komplex ist der geänderte Code (AST-Metriken)? |
| PATTERN | Matcht die Änderung bekannte Anti-Patterns aus historischen Reviews? |

### 2.6 AI Agent Integration (Deterministic Queries)

TheAuditor bietet deterministische Queries als **Ground Truth** für LLMs:

```
Traditionell:                    TheAuditor:
LLM liest 2000 Zeilen Code      LLM ruft: aud query --symbol X --show-callers
LLM rät Beziehungen             LLM bekommt: Fakten aus Index
LLM halluziniert                 LLM kann NICHT halluzinieren (Datenbank-Fakten)
```

**Warum relevant für uns:** Unser Knowledge-Agent könnte eine ähnliche Schnittstelle haben:
- `query --reviewer "Richard Smith" --topic "template instantiation"` → Alle Review-Kommentare von Richard Smith zu Template-Themen
- `query --pr 12345 --show-review-history` → Komplette Review-Historie eines PRs
- `query --pattern "missing const" --frequency` → Wie oft wird dieses Feedback gegeben?

---

## 3. Konkreter Vorschlag: Adaption für C++ Alliance

### 3.1 Database-First Knowledge Store

```
┌─────────────────────────────────────────────────────────┐
│                    KNOWLEDGE PIPELINE                     │
│                                                          │
│  GitHub API ──→ SQLite Index ──→ Vector DB (Pinecone)   │
│  (PRs, Issues,   (Strukturiert,   (Embeddings für       │
│   Comments)       Verifiziert)     Semantic Search)      │
│                                                          │
│  Fidelity Gate:  Fidelity Gate:   Fidelity Gate:        │
│  "7342 PRs        "45891 Comments  "45891 Embeddings    │
│   gescraped"       indexiert"       generiert"           │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Empfohlene Implementierung

| Komponente | Technologie | Begründung |
|------------|-------------|------------|
| Code-Parsing (C++) | `libclang` Python Bindings | Native Clang AST — versteht C++ vollständig |
| Datenbank | SQLite (wie TheAuditor) | Bewährt, kein Server nötig, portable |
| Fidelity System | Manifest-Receipt (eigene Implementierung) | Datenintegrität für 100k+ Records |
| Vector Store | Pinecone (Will's existierender MCP Server) | Bereits vorhanden |
| Agent Queries | Deterministische SQLite-Queries | Ground Truth für LLMs, keine Halluzinationen |

### 3.3 Was wir übernehmen können (Konzeptionell)

| Pattern | Von TheAuditor | Für unser Projekt |
|---------|---------------|-------------------|
| Database-First | SQLite Index statt File-Parsing | PR/Comment Index statt wiederholtes API-Scraping |
| Manifest-Receipt | Fidelity Gates an jeder Pipeline-Grenze | Scrape-Count == Index-Count == Embedding-Count |
| In-Language Extraction | TypeScript Compiler API für JS/TS | `libclang` für C++ |
| Deterministic Queries | `aud query --symbol X` | `query --reviewer X --topic Y` |
| Multi-Vector Convergence | Static + Structural + Process + Flow | History + Expertise + Complexity + Pattern |

### 3.4 Was wir NICHT übernehmen

| Feature | Warum nicht |
|---------|-------------|
| Taint Analysis Engine | Unser Fokus ist PR-Review, nicht Security-Scanning |
| ML Feature Extraction (109-dimensional) | Overkill für Phase 1 — später als Enhancement |
| YAML Refactor Profiles | Nicht relevant für Knowledge Extraction |
| Session Analysis | Wir haben unser eigenes Dashboard dafür |

---

## 4. Nächste Schritte

### Für das Follow-Up Meeting mit Will Pak

1. **Dieses Dokument als Diskussionsgrundlage vorstellen** — "We analyzed an existing tool with a proven database-first architecture and propose adapting key patterns for our LLVM knowledge pipeline"

2. **Frage an Will:** Hat das C++ Alliance Team bereits eine Code-Indexing-Strategie? Nutzen sie `libclang` oder etwas anderes?

3. **Frage an Will:** Wäre ein SQLite-basierter Knowledge Index als Ergänzung zum Pinecone Vector Store sinnvoll? (Strukturierte Queries + Semantic Search = Best of Both Worlds)

4. **Vorschlag:** Fidelity-Verification als Qualitäts-Metrik für die Data Pipeline einführen — "Wir können nachweisen, dass 100% der gescrapten PR-Kommentare korrekt im System gelandet sind"

### Implementierungs-Priorität

| Priorität | Pattern | Aufwand | Impact |
|-----------|---------|---------|--------|
| 🔴 HIGH | Manifest-Receipt für Data Pipeline | 1-2 Tage | Datenintegrität |
| 🔴 HIGH | SQLite Knowledge Index | 2-3 Tage | Instant Queries |
| 🟡 MEDIUM | Deterministic Query Interface | 2-3 Tage | LLM Ground Truth |
| 🟡 MEDIUM | Multi-Vector Convergence | 3-5 Tage | Confidence Scoring |
| 🟢 LOW | libclang Integration | 1-2 Wochen | Deep C++ Understanding |

---

## 5. Referenzen

- [TheAuditor v2.0.4rc1 (archived)](https://github.com/TheAuditorTool/Auditor) — AGPL-3.0
- [Architecture.md](https://github.com/TheAuditorTool/Auditor/blob/main/Architecture.md) — Architektur-Dokumentation
- [Fidelity System Screenshots](#) — Aus Discord-Konversation, 10. Feb 2026
- [libclang Python Bindings](https://libclang.readthedocs.io/) — Für C++ AST Extraction

---

*Dieses Dokument ist ein Vorschlag zur Diskussion. Keine proprietären Informationen aus TheAuditor v3 enthalten. Alle Referenzen beziehen sich auf die öffentlich verfügbare v2.0.4rc1 (AGPL-3.0) und auf allgemeine Architektur-Konzepte.*

*Erstellt: 10. Februar 2026*
