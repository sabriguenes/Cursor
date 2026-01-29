# OpenAI Prompt Engineering Leitfaden

> Der vollständige 2026-Guide für GPT-5, Reasoning-Modelle und mehr

*Von Sabo Guenes | Januar 2026*

Du hast es gehört: "Prompting ist das neue Programmieren." Aber was bedeutet das in der Praxis? Nach einer tiefgehenden Analyse der neuesten OpenAI-Dokumentation und realer Fallstudien (einschließlich Cursors GPT-5-Integration) habe ich alles zusammengestellt, was du wissen musst.

---

## Die Grundlagen

### Was ist Prompt Engineering?

> "Prompt Engineering ist der Prozess, effektive Anweisungen für ein Modell zu schreiben, sodass es konsistent Inhalte generiert, die deinen Anforderungen entsprechen."
> 
> — *OpenAI Dokumentation (übersetzt)*[^1]

Die Kernaussage: Prompting ist **nicht-deterministisch**. Derselbe Prompt kann unterschiedliche Ausgaben produzieren. Dein Ziel ist es, Konsistenz zu maximieren und gleichzeitig Qualität zu erreichen.

### Die Modellauswahl ist entscheidend

OpenAI bietet jetzt zwei grundlegend verschiedene Modellfamilien, die unterschiedliche Prompting-Strategien erfordern:

| Modelltyp | Beispiele | Geeignet für | Prompting-Stil |
|-----------|-----------|--------------|----------------|
| **Reasoning-Modelle** | o3, o4-mini | Komplexe Planung, mehrdeutige Aufgaben | High-Level-Ziele, wenig Details |
| **GPT-Modelle** | GPT-5, GPT-5.2, GPT-4.1 | Schnelle Ausführung, klar definierte Aufgaben | Explizite, detaillierte Anweisungen |

> "Man kann sich den Unterschied zwischen Reasoning- und GPT-Modellen so vorstellen: Ein Reasoning-Modell ist wie ein Senior-Kollege. Du kannst ihm ein Ziel geben und darauf vertrauen, dass er die Details selbst ausarbeitet. Ein GPT-Modell ist wie ein Junior-Kollege. Es arbeitet am besten mit expliziten Anweisungen."
> 
> — *OpenAI Reasoning Best Practices (übersetzt)*[^2]

---

## Prompt Caching: Spare 90% der Kosten

Eine der am wenigsten genutzten Funktionen. Wenn du kein Prompt Caching verwendest, zahlst du zu viel.

### Die Zahlen

| Metrik | Einsparung |
|--------|------------|
| **Latenz** | Bis zu 80% Reduktion |
| **Input-Token-Kosten** | Bis zu 90% Reduktion |

> "Prompt Caching kann die Latenz um bis zu 80% und die Input-Token-Kosten um bis zu 90% reduzieren."
> 
> — *OpenAI Prompt Caching Guide (übersetzt)*[^3]

### Wie es funktioniert

1. Caching ist **automatisch** für Prompts ≥1024 Tokens
2. Funktioniert auf **exakten Präfix-Matches**
3. Cache bleibt typischerweise 5-10 Minuten (in-memory) oder bis zu 24 Stunden (extended)

### Die goldene Regel

```
┌─────────────────────────────────────────┐
│  STATISCHER INHALT (System-Prompt etc.) │  ← Zuerst platzieren
├─────────────────────────────────────────┤
│  DYNAMISCHER INHALT (User-Input etc.)   │  ← Zuletzt platzieren
└─────────────────────────────────────────┘
```

> "Platziere statischen Inhalt wie Anweisungen und Beispiele am Anfang deines Prompts und dynamischen, benutzerspezifischen Inhalt am Ende."
> 
> — *OpenAI Prompt Caching Guide (übersetzt)*[^3]

### Cache-Hit-Raten verbessern

Nutze den `prompt_cache_key` Parameter, um das Routing zu beeinflussen und Cache-Hit-Raten zu verbessern, besonders wenn viele Anfragen lange gemeinsame Präfixe teilen:

```json
{
  "model": "gpt-5.1",
  "input": "Dein Prompt hier...",
  "prompt_cache_key": "my-app-v1"
}
```

### Extended Retention (24h)

Verfügbar für GPT-5.x Modelle:

```json
{
  "model": "gpt-5.1",
  "input": "Dein Prompt hier...",
  "prompt_cache_retention": "24h"
}
```

> **Hinweis:** Extended Caching ist NICHT kompatibel mit Zero Data Retention (ZDR). In-memory Caching ist ZDR-kompatibel.

---

## Message Roles: Die Befehlskette

OpenAI-Modelle folgen einer **Vertrauenshierarchie**:

| Rolle | Priorität | Zweck |
|-------|-----------|-------|
| `developer` | Höchste | Systemregeln, Geschäftslogik |
| `user` | Mittel | Endbenutzer-Eingaben |
| `assistant` | - | Vom Modell generierte Antworten |

> "Developer-Messages sind Anweisungen des Anwendungsentwicklers und werden vor User-Messages priorisiert."
> 
> — *OpenAI Prompt Engineering Guide (übersetzt)*[^1]

### Praktisches Beispiel

```javascript
const response = await client.responses.create({
  model: "gpt-5",
  input: [
    { role: "developer", content: "Sprich wie ein Pirat." },  // Priorität 1
    { role: "user", content: "Sind Semikolons in JavaScript optional?" }  // Priorität 2
  ],
});
```

---

## Formatierung: Markdown + XML

Strukturiere deine Prompts mit klaren Abschnitten:

```markdown
# Identität
Du bist ein Coding-Assistent, der...

# Anweisungen
* Verwende snake_case für Variablennamen
* Keine Markdown-Formatierung in Antworten

# Beispiele
<<user_query>>
Wie deklariere ich eine String-Variable?
<</user_query>>

<<assistant_response>>
var first_name = "Anna";
<</assistant_response>>
```

> "Markdown-Überschriften und Listen können helfen, verschiedene Abschnitte eines Prompts zu markieren und dem Modell eine Hierarchie zu vermitteln."
> 
> — *OpenAI Prompt Engineering Guide (übersetzt)*[^1]

---

## Few-Shot Learning

Few-Shot Learning ermöglicht es, ein Modell auf eine neue Aufgabe zu lenken, indem einige Input/Output-Beispiele im Prompt enthalten sind. Das Modell "erkennt" das Muster und wendet es auf neue Eingaben an.

### Wann Few-Shot nutzen

- Klassifizierungsaufgaben (Sentiment, Kategorie, Priorität)
- Formatierungsanforderungen (spezifische Ausgabestruktur)
- Domänenspezifische Terminologie
- Edge-Case-Handling

### Beispiel: IT-Ticket-Kategorisierung

```markdown
# Anweisungen
Kategorisiere das folgende Support-Ticket in: Hardware, Software oder Sonstiges.
Antworte nur mit einem dieser Wörter.

# Beispiele
<<ticket id="example-1">>
Mein Monitor geht nach dem Umzug an einen anderen Platz nicht mehr an. Die Power-LED bleibt aus.
<</ticket>>

<<assistant_response id="example-1">>
Hardware
<</assistant_response>>

<<ticket id="example-2">>
Nach dem Update stürzt die App direkt beim Start ab (Fehlercode 0x0004).
<</ticket>>

<<assistant_response id="example-2">>
Software
<</assistant_response>>

<<ticket id="example-3">>
Was sind gute Restaurants in München für ein Team-Dinner?
<</ticket>>

<<assistant_response id="example-3">>
Sonstiges
<</assistant_response>>
```

> **Tipp:** Zeige bei Beispielen eine diverse Bandbreite möglicher Eingaben mit den gewünschten Ausgaben. Decke Edge Cases ab.

---

## Retrieval-Augmented Generation (RAG)

RAG ist die Technik, relevante Kontextinformationen zum Prompt hinzuzufügen, die das Modell zur Antwortgenerierung nutzen kann.

### Warum RAG nutzen?

- Zugriff auf **proprietäre Daten** außerhalb des Trainingssets
- Antworten auf **spezifische Quellen** beschränken
- Antworten **aktuell halten** mit neuen Informationen

### Implementierung

1. **Wissensbasis abfragen** (Vektordatenbank, Dateisuche, etc.)
2. **Abgerufenen Kontext** in den Prompt einfügen
3. **Kontext referenzieren** in deinen Anweisungen

```markdown
# Anweisungen
Beantworte die Frage des Users NUR basierend auf dem bereitgestellten Kontext.
Wenn die Antwort nicht im Kontext ist, sage "Diese Information habe ich nicht."

# Kontext
<<document source="internes-wiki">>
Unsere Rückgaberichtlinie erlaubt Rückgaben innerhalb von 30 Tagen nach Kauf.
Artikel müssen ungeöffnet und in Originalverpackung sein.
Digitale Produkte sind nicht erstattungsfähig.
<</document>>

# User-Frage
Kann ich eine Software-Lizenz zurückgeben, die ich letzte Woche gekauft habe?
```

### Praktische Tipps

- Platziere den abgerufenen Kontext **vor** der User-Frage.
- Halte den Kontext **kurz und relevant** (Noise entfernen).
- Wenn du Nachvollziehbarkeit brauchst: **Zitate/Quellen** (Doc-IDs, URLs oder Snippets) in den Kontext aufnehmen und verlangen, dass das Modell darauf referenziert.

---

## Responses API vs Chat Completions

OpenAI bietet zwei APIs für Textgenerierung. Für GPT-5 wird die **Responses API** stark empfohlen.

### Hauptunterschiede

| Feature | Responses API | Chat Completions |
|---------|---------------|------------------|
| **Reasoning-Persistenz** | Reasoning-Items zwischen Turns erhalten | Stateless, keine Persistenz |
| **Agentic Performance** | Optimiert für Multi-Turn Tool-Calling | Basis-Tool-Support |
| **Vorheriger Kontext** | `previous_response_id` nutzen | Manuelle Message-Verwaltung |
| **Empfohlen für** | GPT-5, agentic Workflows | Legacy-Anwendungen |

### Performance-Auswirkung

> "Wir beobachteten Tau-Bench Retail Score-Verbesserungen von 73,9% auf 78,2% allein durch den Wechsel zur Responses API und die Nutzung von `previous_response_id`."
> 
> — *OpenAI GPT-5 Prompting Guide (übersetzt)*[^4]

### Migrations-Beispiel

**Chat Completions (Alt):**
```javascript
const response = await client.chat.completions.create({
  model: "gpt-5",
  messages: [
    { role: "system", content: "Du bist ein hilfreicher Assistent." },
    { role: "user", content: "Hallo!" }
  ]
});
```

**Responses API (Neu):**
```javascript
const response = await client.responses.create({
  model: "gpt-5",
  input: [
    { role: "developer", content: "Du bist ein hilfreicher Assistent." },
    { role: "user", content: "Hallo!" }
  ]
});
```

---

## GPT-5: Spezifische Best Practices

GPT-5 ist OpenAIs bisher am besten steuerbare Modell. So holst du das Maximum heraus.

### Verbosity Steuerung

GPT-5 führt einen neuen `verbosity` API-Parameter ein, der die Länge der finalen Antworten steuert (nicht des Reasonings):

| Wert | Effekt |
|------|--------|
| `low` | Kurze Antworten, minimale Erklärungen |
| `medium` | Ausgewogen (Standard) |
| `high` | Ausführliche Erklärungen und Kontext |

Du kannst diesen global gesetzten Parameter mit natürlichsprachlichen Anweisungen in spezifischen Kontexten überschreiben. Zum Beispiel: Setze `verbosity: "low"` global, aber füge "Verwende hohe Ausführlichkeit für Code" in deinem Prompt hinzu.

### Agentic Eagerness kontrollieren

GPT-5 kann von "vor jeder Aktion fragen" bis zu "vollständiger Autonomie" konfiguriert werden.

#### Für weniger Eagerness (schneller, günstiger)

```xml
<<context_gathering>>
Ziel: Kontext schnell erfassen. Discovery parallelisieren und stoppen, sobald gehandelt werden kann.
Methode:
- Breit starten, dann zu fokussierten Subqueries auffächern.
- Übermäßiges Suchen nach Kontext vermeiden.
Frühe Stopp-Kriterien:
- Der exakte zu ändernde Inhalt kann benannt werden.
- Top-Hits konvergieren (~70%) auf einen Bereich/Pfad.
<</context_gathering>>
```

> — *OpenAI GPT-5 Prompting Guide*[^4]

#### Für mehr Eagerness (volle Autonomie)

```xml
<persistence>
- Du bist ein Agent - arbeite weiter, bis die Anfrage des Users vollständig gelöst ist
- Beende deinen Turn nur, wenn du sicher bist, dass das Problem gelöst ist
- Stoppe niemals oder gib an den User zurück, wenn du auf Unsicherheit triffst
- Frage nicht nach Bestätigung oder Klärung von Annahmen
</persistence>
```

> — *OpenAI GPT-5 Prompting Guide*[^4]

### Tool Preambles

Für bessere Benutzererfahrung bei lang laufenden Aufgaben:

```xml
<<tool_preambles>>
- Beginne immer mit einer freundlichen, klaren Umformulierung des User-Ziels
- Skizziere einen strukturierten Plan mit jedem logischen Schritt
- Erzähle jeden Schritt kurz und sequenziell
- Fasse am Ende die erledigte Arbeit zusammen
<</tool_preambles>>
```

> — *OpenAI GPT-5 Prompting Guide*[^4]

### Self-Reflection Rubrics

Für Zero-to-One App-Generierung:

```xml
<<self_reflection>>
- Erstelle zuerst eine Rubrik, bis du dir sicher bist.
- Erstelle eine Rubrik mit 5-7 Kategorien. Nur für interne Zwecke.
- Nutze die Rubrik, um auf die bestmögliche Lösung zu iterieren.
- Wenn nicht alle Kategorien top bewertet sind, von vorne beginnen.
<</self_reflection>>
```

> — *OpenAI GPT-5 Prompting Guide*[^4]

---

## Fallstudie: Cursors GPT-5-Integration

Cursor (der AI Code Editor) war Alpha-Tester für GPT-5. Ihre Erkenntnisse sind unbezahlbar.

### Problem: Zu ausführliche Ausgaben

GPT-5 produzierte zu viele Status-Updates, die den Benutzerfluss störten.

### Lösung: Duale Verbosity-Steuerung

1. API `verbosity` Parameter auf `low` global setzen
2. Prompt-Anweisung für ausführlichen **Code** hinzufügen:

```
Schreibe Code für Klarheit zuerst. Bevorzuge lesbare, wartbare Lösungen 
mit klaren Namen, Kommentaren wo nötig, und unkompliziertem Kontrollfluss. 
Verwende hohe Ausführlichkeit für das Schreiben von Code und Code-Tools.
```

> — *Cursor Team, via OpenAI GPT-5 Prompting Guide*[^4]

### Problem: Zu viele Rückfragen

GPT-5 fragte unnötig beim User nach.

### Lösung: Explizite Autonomie-Anweisungen

```
Beachte, dass die Code-Änderungen dem User als vorgeschlagene Änderungen 
angezeigt werden, was bedeutet (a) deine Code-Änderungen können proaktiv 
sein, da der User immer ablehnen kann, und (b) dein Code sollte gut 
geschrieben und leicht zu überprüfen sein.

Wenn du nächste Schritte vorschlägst, die Codeänderungen beinhalten würden,
führe diese proaktiv aus, anstatt zu fragen, ob fortgefahren werden soll.
```

> — *Cursor Team, via OpenAI GPT-5 Prompting Guide*[^4]

### Warnung: Widersprüchliche Anweisungen

> "GPT-5s sorgfältiges Instruction-Following bedeutet, dass schlecht konstruierte Prompts mit widersprüchlichen oder vagen Anweisungen schädlicher für GPT-5 sein können als für andere Modelle, da es Reasoning-Tokens verbraucht, um die Widersprüche aufzulösen."
> 
> — *OpenAI GPT-5 Prompting Guide (übersetzt)*[^4]

**Überprüfe deine Prompts auf Konflikte vor dem Deployment!**

---

## Reasoning-Modelle: Andere Regeln gelten

Für o3, o4-mini und andere Reasoning-Modelle gilt: **Vergiss alles, was du über Chain-of-Thought Prompting weißt**.

### Reasoning Effort Stufen

Der `reasoning_effort` Parameter steuert, wie intensiv das Modell nachdenkt:

| Stufe | Anwendungsfall | Trade-off |
|-------|----------------|-----------|
| `minimal` | Latenz-kritisch, einfache Aufgaben | Schnellste Option, profitiert von GPT-4.1 Prompting-Patterns |
| `low` | Schnelle Entscheidungen | Schnell mit etwas Reasoning |
| `medium` | Standard, ausgewogen | Gut für die meisten Aufgaben |
| `high` | Komplexe Multi-Step-Aufgaben | Am gründlichsten, höhere Latenz |

> **Tipp:** Bei `minimal` Reasoning: Fordere das Modell auf, eine kurze Erklärung am Anfang der Antwort zu geben (z.B. Stichpunkte), um die Performance zu verbessern.

### Das solltest du NICHT tun

```
❌ "Denke Schritt für Schritt"
❌ "Erkläre dein Vorgehen"
❌ "Zeige deinen Lösungsweg"
```

> "Da diese Modelle intern denken, ist es unnötig, sie aufzufordern, 'Schritt für Schritt zu denken' oder 'ihr Vorgehen zu erklären'."
> 
> — *OpenAI Reasoning Best Practices (übersetzt)*[^2]

### Das solltest du stattdessen tun

- Halte Prompts **einfach und direkt**
- Probiere **Zero-Shot zuerst** (keine Beispiele)
- Verwende Delimiter (XML, Markdown) für Struktur
- Sei spezifisch bei Constraints

### Wann Reasoning-Modelle verwenden

| Anwendungsfall | Warum es funktioniert |
|----------------|----------------------|
| **Mehrdeutigkeit navigieren** | Versteht Intent aus wenig Information |
| **Nadel im Heuhaufen** | Findet relevante Info in riesigen Datensätzen |
| **Komplexe Dokumente** | Rechtsverträge, Finanzberichte |
| **Agentic Planning** | Multi-Step-Strategieentwicklung |
| **Visual Reasoning** | Komplexe Charts, Architekturzeichnungen |
| **Code Review** | Entdeckt subtile Bugs |
| **LLM-as-Judge** | Bewertung anderer Modell-Outputs |

> "Wir haben GPT-4o durch o1 ersetzt und festgestellt, dass o1 viel besser darin ist, über das Zusammenspiel zwischen Dokumenten zu schlussfolgern und logische Schlüsse zu ziehen, die in keinem einzelnen Dokument offensichtlich waren. Als Ergebnis sahen wir eine 4-fache Verbesserung der End-to-End-Performance."
> 
> — *Blue J (Steuerforschungsplattform), via OpenAI (übersetzt)*[^2]

### Visual Reasoning

o1 ist das einzige Reasoning-Modell mit Vision-Fähigkeiten. Es versteht komplexe Visualisierungen, bei denen GPT-4o Schwierigkeiten hat:

| Visueller Typ | o1 Vorteil |
|---------------|------------|
| Architekturzeichnungen | Identifiziert Einrichtungen, Materialien, liest Legenden über Seiten |
| Finanzcharts | Versteht Beziehungen zwischen Datenpunkten |
| Komplexe Tabellen | Parst mehrdeutige Strukturen |
| Schlechte Bildqualität | Bessere OCR und Interpretation |

> "GPT-4o erreichte 50% Genauigkeit bei unseren schwierigsten Bildklassifizierungsaufgaben. o1 erreichte beeindruckende 88% Genauigkeit ohne Änderungen an unserer Pipeline."
> 
> — *SafetyKit (Risiko- & Compliance-Plattform), via OpenAI (übersetzt)*[^2]

### Weitere Kundenerfolgsstorys

| Unternehmen | Anwendungsfall | Ergebnis |
|-------------|----------------|----------|
| **Hebbia** | Komplexe Rechtsdokumentanalyse | "o1 lieferte bessere Ergebnisse bei 52% der komplexen Prompts" |
| **Endex** | M&A Due Diligence | Fand kritische $75M-Darlehensklausel in Fußnoten |
| **BlueFlame AI** | Aktionärs-Equity-Berechnungen | Löste komplexe Anti-Dilution-Loops fehlerfrei |
| **Lindy.AI** | Agentic Workflows (E-Mail, Kalender) | "Agents wurden über Nacht praktisch fehlerfrei" |
| **CodeRabbit** | AI Code Reviews | 3x Steigerung der Produktkonversionsraten |
| **Windsurf** | Komplexes Software-Design | "Produziert konstant hochwertigen, schlüssigen Code" |
| **Braintrust** | LLM-as-Judge Evaluierungen | F1-Score verbesserte sich von 0,12 auf 0,74 |

---

## Frontend-Entwicklung: Empfohlener Stack

Für GPT-5 Frontend-Projekte empfiehlt OpenAI:

| Kategorie | Empfohlen |
|-----------|-----------|
| **Framework** | Next.js (TypeScript), React |
| **Styling** | Tailwind CSS, shadcn/ui, Radix Themes |
| **Icons** | Material Symbols, Heroicons, Lucide |
| **Animation** | Motion |
| **Fonts** | Sans Serif, Inter, Geist, Mona Sans, IBM Plex Sans, Manrope |

> — *OpenAI GPT-5 Prompting Guide*[^4]

### Frontend Code Editing Rules

Für konsistenten, hochwertigen Frontend-Code nutze strukturierte Prompts wie diesen:

```xml
<<code_editing_rules>>
<<guiding_principles>>
- Klarheit und Wiederverwendung: Jede Komponente sollte modular und wiederverwendbar sein
- Konsistenz: Einem einheitlichen Design-System folgen
- Einfachheit: Kleine, fokussierte Komponenten bevorzugen
- Visuelle Qualität: Best Practices für Spacing, Padding, Hover-States befolgen
<</guiding_principles>>

<<frontend_stack_defaults>>
- Framework: Next.js (TypeScript)
- Styling: TailwindCSS
- UI-Komponenten: shadcn/ui
- Icons: Lucide
- State Management: Zustand
- Verzeichnisstruktur:
  /src
    /app/api/<route>/route.ts  # API-Endpunkte
    /(pages)                   # Seiten-Routes
    /components/               # UI-Bausteine
    /hooks/                    # Wiederverwendbare React-Hooks
    /lib/                      # Utilities
    /stores/                   # Zustand-Stores
    /types/                    # Geteilte TypeScript-Types
<</frontend_stack_defaults>>

<<ui_ux_best_practices>>
- Visuelle Hierarchie: Typografie auf 4-5 Schriftgrößen begrenzen
- Farbnutzung: 1 neutrale Basis + bis zu 2 Akzentfarben
- Abstände: Immer Vielfache von 4 für Padding/Margins
- State-Handling: Skeleton-Platzhalter für Ladezeiten
- Barrierefreiheit: Semantisches HTML und ARIA-Rollen
<</ui_ux_best_practices>>
<</code_editing_rules>>
```

> — *OpenAI GPT-5 Prompting Guide*[^4]

---

## Tooling: Prompt Optimizer & Evals

### Prompt Optimizer

OpenAIs Dashboard-Tool für automatische Prompt-Verbesserung:

1. Dataset mit Prompt + Evaluationsdaten erstellen
2. Annotations (Good/Bad) + Kritiken hinzufügen
3. "Optimize" klicken → neue verbesserte Version

> "Der Prompt Optimizer ist ein Chat-Interface im Dashboard, in dem du einen Prompt eingibst und wir ihn nach aktuellen Best Practices optimieren."
> 
> — *OpenAI Prompt Optimizer Guide (übersetzt)*[^5]

### Evaluations (Evals)

Teste deine Prompts systematisch:

1. Erfolgskriterien definieren (Graders)
2. Test-Datasets erstellen
3. Evals bei Prompt-Änderungen ausführen
4. Basierend auf Ergebnissen iterieren

> "Evaluations testen Modell-Outputs, um sicherzustellen, dass sie deinen Stil- und Inhaltskriterien entsprechen. Evals zu schreiben ist eine essentielle Komponente beim Aufbau zuverlässiger Anwendungen."
> 
> — *OpenAI Evals Guide (übersetzt)*[^6]

#### Eval via API erstellen

```python
from openai import OpenAI
client = OpenAI()

eval_obj = client.evals.create(
    name="IT-Ticket-Kategorisierung",
    data_source_config={
        "type": "custom",
        "item_schema": {
            "type": "object",
            "properties": {
                "ticket_text": {"type": "string"},
                "correct_label": {"type": "string"},
            },
            "required": ["ticket_text", "correct_label"],
        },
        "include_sample_schema": True,
    },
    testing_criteria=[
        {
            "type": "string_check",
            "name": "Output mit menschlichem Label abgleichen",
            "input": "{{ sample.output_text }}",
            "operation": "eq",
            "reference": "{{ item.correct_label }}",
        }
    ],
)
```

#### Testdaten-Format (JSONL)

```jsonl
{"item": {"ticket_text": "Mein Monitor geht nicht an!", "correct_label": "Hardware"}}
{"item": {"ticket_text": "Ich bin in vim und kann nicht beenden!", "correct_label": "Software"}}
{"item": {"ticket_text": "Beste Restaurants in München?", "correct_label": "Sonstiges"}}
```

#### Eval ausführen

```python
run = client.evals.runs.create(
    "YOUR_EVAL_ID",
    name="Kategorisierungs-Testlauf",
    data_source={
        "type": "responses",
        "model": "gpt-4.1",
        "input_messages": {
            "type": "template",
            "template": [
                {"role": "developer", "content": "Kategorisiere in Hardware, Software oder Sonstiges."},
                {"role": "user", "content": "{{ item.ticket_text }}"},
            ],
        },
        "source": {"type": "file_id", "id": "YOUR_FILE_ID"},
    },
)
```

---

## Praktische Empfehlungen

### 1. Modellversionen fixieren

```javascript
model: "gpt-4.1-2025-04-14"  // ✅ Spezifischer Snapshot
model: "gpt-4.1"             // ⚠️ Verhalten kann sich ändern
```

### 2. Evals früh aufbauen

Warte nicht bis zur Produktion, um Edge Cases zu entdecken.

### 3. Wiederverwendbare Prompts nutzen

Speichere Prompts mit Versionierung im OpenAI Dashboard:

```javascript
prompt: {
  id: "pmpt_abc123",
  version: "2",
  variables: { customer_name: "Max Mustermann" }
}
```

### 4. Cached Token Usage überwachen

Prüfe `usage.prompt_tokens_details.cached_tokens` um Caching zu verifizieren.

### 5. Metaprompting verwenden

Lass GPT-5 seine eigenen Prompts verbessern:

```
Hier ist ein Prompt: [PROMPT]
Das gewünschte Verhalten ist [X], stattdessen passiert [Y]. 
Welche minimalen Änderungen würdest du machen, um das gewünschte Verhalten 
konsistent zu erreichen?
```

> — *OpenAI GPT-5 Prompting Guide*[^4]

---

## Referenzen

[^1]: OpenAI. "Prompt Engineering." *OpenAI Platform Documentation*, Januar 2026. https://platform.openai.com/docs/guides/prompt-engineering

[^2]: OpenAI. "Reasoning Best Practices." *OpenAI Platform Documentation*, Januar 2026. https://platform.openai.com/docs/guides/reasoning-best-practices

[^3]: OpenAI. "Prompt Caching." *OpenAI Platform Documentation*, Januar 2026. https://platform.openai.com/docs/guides/prompt-caching

[^4]: OpenAI. "GPT-5 Prompting Guide." *OpenAI Cookbook*, August 2025. https://cookbook.openai.com/examples/gpt-5/gpt-5_prompting_guide

[^5]: OpenAI. "Prompt Optimizer." *OpenAI Platform Documentation*, Januar 2026. https://platform.openai.com/docs/guides/prompt-optimizer

[^6]: OpenAI. "Working with Evals." *OpenAI Platform Documentation*, Januar 2026. https://platform.openai.com/docs/guides/evals

---

*Fragen? Kontaktiere mich auf [cursorconsulting.org](https://cursorconsulting.org)*
