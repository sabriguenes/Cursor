# Anthropic Claude Prompt Engineering Leitfaden

> Der vollständige 2026-Guide für Claude Opus 4.5, Sonnet 4.5 und Agentic Workflows

*Von Sabo Guenes | Januar 2026*

Claude 4.5 Modelle repräsentieren einen bedeutenden Sprung in KI-Fähigkeiten. Aber mit großer Leistung kommt die Notwendigkeit für präzises Prompting. Nach Analyse der offiziellen Anthropic-Dokumentation und Engineering-Blog-Beiträge habe ich alles zusammengestellt, was du über effektives Claude-Prompting wissen musst.

---

## Die Grundlagen

### Was macht Claude 4.5 anders?

Claude 4.5 Modelle wurden für **präziseres Instruction Following** trainiert als vorherige Generationen. Das ist sowohl eine Stärke als auch etwas, worauf man achten sollte.

> "Diese Modelle wurden für präziseres Instruction Following trainiert als vorherige Generationen von Claude-Modellen."
> 
> — *Anthropic Claude 4 Best Practices (übersetzt)*[^1]

### Modellauswahl

| Modell | Geeignet für | Eigenschaften |
|--------|--------------|---------------|
| **Opus 4.5** | Komplexes Coding, Agents, Long-Horizon Tasks | Am leistungsfähigsten, Effort-Parameter verfügbar |
| **Sonnet 4.5** | Ausgewogene Performance, Alltagsaufgaben | Schnell, kosteneffizient |
| **Haiku 4.5** | Schnelle Antworten, hohes Volumen | Am schnellsten, günstigste Kosten |

> "Es ist intelligent, effizient und das beste Modell der Welt für Coding, Agents und Computer Use."
> 
> — *Anthropic Claude Opus 4.5 Announcement (übersetzt)*[^2]

---

## Allgemeine Prinzipien

### Sei explizit mit deinen Anweisungen

Claude 4.5 Modelle reagieren gut auf klare, explizite Anweisungen. Spezifisch zu sein verbessert die Ergebnisse.

> "Claude 4.x Modelle reagieren gut auf klare, explizite Anweisungen. Spezifisch zu sein über den gewünschten Output kann die Ergebnisse verbessern."
> 
> — *Anthropic Claude 4 Best Practices (übersetzt)*[^1]

**Statt:**
```
Erstelle ein Analytics-Dashboard
```

**Versuche:**
```
Erstelle ein Analytics-Dashboard. Füge so viele relevante Features und Interaktionen wie möglich ein. Gehe über die Basics hinaus und erstelle eine voll ausgestattete Implementierung.
```

### Füge Kontext für bessere Performance hinzu

Kontext oder Motivation hinter deinen Anweisungen hilft Claude, deine Ziele zu verstehen.

```
Formatiere deine Antwort als Stichpunkte weil:
1. Das wird in einer Präsentation verwendet
2. Führungskräfte müssen schnell scannen können
3. Jeder Punkt sollte umsetzbar sein
```

> "Kontext oder Motivation hinter deinen Anweisungen zu liefern, wie zum Beispiel zu erklären warum dieses Verhalten wichtig ist, kann Claude 4.x Modellen helfen, deine Ziele besser zu verstehen."
> 
> — *Anthropic Claude 4 Best Practices (übersetzt)*[^1]

---

## XML Tags: Claudes native Sprache

Claude wurde mit XML-lastigen Daten trainiert. XML Tags verbessern dramatisch Prompt-Struktur und Output-Qualität.

> "Nutze Tags wie `<instructions>`, `<example>` und `<formatting>` um verschiedene Teile deines Prompts klar zu trennen. Das verhindert, dass Claude Anweisungen mit Beispielen oder Kontext verwechselt."
> 
> — *Anthropic XML Tags Guide (übersetzt)*[^3]

### Warum XML Tags nutzen?

| Vorteil | Beschreibung |
|---------|--------------|
| **Klarheit** | Trenne verschiedene Prompt-Teile klar |
| **Genauigkeit** | Reduziere Fehler durch Fehlinterpretation |
| **Flexibilität** | Einfach Abschnitte modifizieren ohne alles neu zu schreiben |
| **Parsebarkeit** | Extrahiere spezifische Teile aus Antworten |

### Praktisches Beispiel

```xml
<instructions>
Analysiere den folgenden Vertrag auf potenzielle Risiken.
Fokussiere auf Haftungsklauseln und Kündigungsbedingungen.
</instructions>

<contract>
{{VERTRAGSTEXT}}
</contract>

<output_format>
Gib deine Analyse als JSON zurück mit Keys: risks, severity, recommendations
</output_format>
```

### Tagging Best Practices

1. **Sei konsistent**: Nutze die gleichen Tag-Namen durchgehend
2. **Verschachtele Tags**: Nutze Hierarchie für komplexe Inhalte: `<outer><inner></inner></outer>`
3. **Referenziere Tags**: "Unter Verwendung des Vertrags in `<contract>` Tags..."

> "Kombiniere XML Tags mit anderen Techniken wie Multishot Prompting (`<examples>`) oder Chain of Thought (`<thinking>`, `<answer>`). Das erstellt super-strukturierte, hochperformante Prompts."
> 
> — *Anthropic XML Tags Guide (übersetzt)*[^3]

---

## System Prompts: Die mächtigste Technik

Role Prompting via System Prompts ist die mächtigste Methode, Claudes Verhalten zu formen.

> "Role Prompting ist die mächtigste Methode, System Prompts mit Claude zu nutzen. Die richtige Rolle kann Claude von einem allgemeinen Assistenten in deinen virtuellen Domain-Experten verwandeln!"
> 
> — *Anthropic System Prompts Guide (übersetzt)*[^4]

### Warum Role Prompting nutzen?

- **Verbesserte Genauigkeit** bei komplexen Szenarien (Rechts-, Finanzanalyse)
- **Angepasster Ton** (CFO-Kürze vs. Texter-Flair)
- **Verbesserter Fokus** auf aufgabenspezifische Anforderungen

### Implementierung

```python
import anthropic
client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-opus-4-5-20251101",
    max_tokens=2048,
    system="Du bist ein erfahrener Data Scientist bei einem DAX-Konzern.",
    messages=[
        {"role": "user", "content": "Analysiere diesen Datensatz auf Anomalien..."}
    ]
)
```

### Role Prompting Tipps

- Rolle in `system` Parameter definieren
- Aufgabenspezifische Anweisungen in `user` Turn
- Experimentiere mit Spezifität: "Data Scientist" vs. "Data Scientist spezialisiert auf Customer Insight Analyse für DAX-Konzerne"

---

## Chain of Thought (CoT) Prompting

Claude Raum zum Nachdenken zu geben verbessert dramatisch die Performance bei komplexen Aufgaben.

> "Schrittweises Durcharbeiten von Problemen reduziert Fehler, besonders in Mathe, Logik, Analyse oder generell komplexen Aufgaben."
> 
> — *Anthropic Chain of Thought Guide (übersetzt)*[^5]

### Drei CoT-Methoden

| Methode | Komplexität | Anwendungsfall |
|---------|-------------|----------------|
| **Basic** | Niedrig | Einfache Reasoning-Aufgaben |
| **Guided** | Mittel | Spezifische Denkschritte nötig |
| **Structured** | Hoch | Trennung von Denken und Antwort nötig |

### Basic CoT

```
Denke Schritt für Schritt über dieses Problem nach.
```

### Guided CoT

```
Denke über dieses Problem nach, indem du:
1. Die Schlüsselvariablen identifizierst
2. Edge Cases berücksichtigst
3. Eine Lösung vorschlägst
4. Deine Lösung validierst
```

### Structured CoT (Empfohlen)

```xml
<instructions>
Analysiere diese Finanzdaten. Zeige dein Reasoning in <thinking> Tags,
dann liefere deine finale Antwort in <answer> Tags.
</instructions>

<data>
{{FINANZDATEN}}
</data>
```

**Output:**
```xml
<thinking>
Zuerst untersuche ich die Umsatztrends...
Der Q3-Einbruch korreliert mit...
Das deutet darauf hin...
</thinking>

<answer>
Das Unternehmen zeigt starke Fundamentaldaten mit einer temporären
Q3-Verlangsamung aufgrund saisonaler Faktoren. Empfehlung: Halten mit positivem Ausblick.
</answer>
```

> "Lass Claude immer sein Denken ausgeben. Ohne die Ausgabe des Denkprozesses findet kein Denken statt!"
> 
> — *Anthropic Chain of Thought Guide (übersetzt)*[^5]

---

## Extended Thinking für komplexe Aufgaben

Für die anspruchsvollsten Probleme bietet Claudes Extended Thinking Mode logarithmische Genauigkeitsverbesserungen.

> "Claude performt oft besser mit High-Level-Anweisungen, einfach tief über eine Aufgabe nachzudenken, als mit schrittweiser präskriptiver Anleitung."
> 
> — *Anthropic Extended Thinking Tips (übersetzt)*[^6]

### Wann Extended Thinking nutzen

- Komplexe MINT-Probleme
- Constraint-Optimierung
- Multi-Step-Analyse
- Code-Architektur-Entscheidungen

### Kernaussage: Weniger Vorschriften, mehr Freiheit

**Statt:**
```
Denke über dieses Mathe-Problem Schritt für Schritt nach:
1. Zuerst identifiziere die Variablen
2. Dann stelle die Gleichung auf
3. Als nächstes löse nach x auf
...
```

**Versuche:**
```
Bitte denke gründlich und sehr detailliert über dieses Mathe-Problem nach.
Erwäge mehrere Ansätze und zeige dein vollständiges Reasoning.
Probiere verschiedene Methoden, wenn dein erster Ansatz nicht funktioniert.
```

### Technische Überlegungen

- Minimales Thinking-Budget: 1024 Tokens
- Starte klein, erhöhe nach Bedarf
- Für >32K Thinking-Tokens: Batch Processing nutzen
- Extended Thinking performt am besten auf Englisch

> "Die Kreativität des Modells beim Angehen von Problemen kann die Fähigkeit eines Menschen übersteigen, den optimalen Denkprozess vorzuschreiben."
> 
> — *Anthropic Extended Thinking Tips (übersetzt)*[^6]

---

## Opus 4.5 Spezifische Best Practices

### Der Effort-Parameter

Einzigartig für Opus 4.5 ermöglicht der Effort-Parameter die Kontrolle von Token-Nutzung vs. Gründlichkeit.

> "Mit unserem neuen Effort-Parameter in der Claude API kannst du entscheiden, ob du Zeit und Kosten minimieren oder Fähigkeiten maximieren willst."
> 
> — *Anthropic Claude Opus 4.5 Announcement (übersetzt)*[^2]

| Effort-Stufe | Anwendungsfall | Token-Auswirkung |
|--------------|----------------|------------------|
| Low | Schnelle Entscheidungen | Schnellste, günstigste |
| Medium | Ausgewogene Aufgaben | Entspricht Sonnet 4.5 Qualität |
| High | Komplexe Analyse | Am gründlichsten |

### Achte auf Overengineering

Opus 4.5 neigt dazu, zusätzliche Dateien zu erstellen, unnötige Abstraktionen hinzuzufügen oder Flexibilität einzubauen, die nicht angefordert wurde.

```xml
<<avoid_overengineering>>
Vermeide Over-Engineering. Mache nur Änderungen, die direkt angefordert wurden
oder eindeutig notwendig sind. Halte Lösungen einfach und fokussiert.

Füge keine Features hinzu, refaktoriere keinen Code und mache keine 
"Verbesserungen" über das Angeforderte hinaus. Ein Bug-Fix braucht 
keinen aufgeräumten umgebenden Code.

Erstelle keine Helpers, Utilities oder Abstraktionen für einmalige Operationen.
<</avoid_overengineering>>
```

> "Claude Opus 4.5 hat eine Tendenz zum Overengineering durch Erstellen zusätzlicher Dateien, Hinzufügen unnötiger Abstraktionen oder Einbauen von Flexibilität, die nicht angefordert wurde."
> 
> — *Anthropic Claude 4 Best Practices (übersetzt)*[^1]

### System Prompt Sensibilität

Opus 4.5 reagiert stärker auf System Prompts als vorherige Modelle. Wenn deine Prompts darauf ausgelegt waren, Undertriggering zu reduzieren, siehst du jetzt möglicherweise Overtriggering.

**Statt:**
```
KRITISCH: Du MUSST dieses Tool verwenden wenn...
```

**Versuche:**
```
Verwende dieses Tool wenn...
```

> "Wenn deine Prompts darauf ausgelegt waren, Undertriggering bei Tools oder Skills zu reduzieren, kann Claude Opus 4.5 jetzt overtriggern. Die Lösung ist, aggressive Sprache zurückzufahren."
> 
> — *Anthropic Claude 4 Best Practices (übersetzt)*[^1]

### Thinking-Sensibilität

Wenn Extended Thinking deaktiviert ist, reagiert Opus 4.5 empfindlich auf das Wort "think" (denken).

**Ersetze:**
- "think" → "consider", "evaluate", "analyze"
- "denke über" → "reflektiere über", "untersuche"

---

## Effektive Agents bauen

### Workflows vs. Agents

Anthropic unterscheidet zwischen zwei Arten von agentischen Systemen:

| Typ | Beschreibung | Wann nutzen |
|-----|--------------|-------------|
| **Workflows** | LLMs orchestriert durch vordefinierte Code-Pfade | Vorhersehbare, gut definierte Aufgaben |
| **Agents** | LLMs steuern dynamisch ihre eigenen Prozesse | Flexibilität nötig, offene Probleme |

> "Workflows sind Systeme, in denen LLMs und Tools durch vordefinierte Code-Pfade orchestriert werden. Agents sind Systeme, in denen LLMs dynamisch ihre eigenen Prozesse und Tool-Nutzung steuern."
> 
> — *Anthropic Building Effective Agents (übersetzt)*[^7]

### Gängige Workflow-Patterns

#### 1. Prompt Chaining

Teile Aufgaben in sequentielle Schritte:

```
Input → LLM Call 1 → Gate Check → LLM Call 2 → Output
```

**Nutze für:** Marketing-Text-Generierung → Übersetzung

#### 2. Routing

Klassifiziere Input und leite an spezialisierte Handler:

```
Input → Classifier → [Handler A | Handler B | Handler C] → Output
```

**Nutze für:** Kundenservice (allgemeine Fragen vs. Erstattungen vs. technischer Support)

#### 3. Parallelisierung

Führe mehrere LLM-Calls gleichzeitig aus:

- **Sectioning**: Teile Aufgabe in unabhängige Teilaufgaben
- **Voting**: Führe gleiche Aufgabe mehrfach für Konfidenz aus

**Nutze für:** Code-Review (mehrere Vulnerability-Checks), Content-Moderation

#### 4. Orchestrator-Workers

Zentrales LLM teilt Aufgaben dynamisch auf und delegiert:

```
Input → Orchestrator → [Worker 1, Worker 2, ...] → Synthesize → Output
```

**Nutze für:** Komplexe Coding-Aufgaben, Multi-Source-Research

### Agent Design Prinzipien

1. **Halte Einfachheit** im Agent-Design aufrecht
2. **Priorisiere Transparenz** durch Anzeigen von Planungsschritten
3. **Gestalte dein ACI** (Agent-Computer Interface) durch gründliche Tool-Dokumentation

> "Erfolg im LLM-Bereich geht nicht darum, das raffinierteste System zu bauen. Es geht darum, das richtige System für deine Bedürfnisse zu bauen."
> 
> — *Anthropic Building Effective Agents (übersetzt)*[^7]

---

## Long-Horizon Reasoning

Claude 4.5 Modelle glänzen bei Aufgaben, die sich über erweiterte Sessions und mehrere Context Windows erstrecken.

### State Tracking Best Practices

| Methode | Nutze für |
|---------|-----------|
| **JSON-Dateien** | Strukturierte Daten (Testergebnisse, Aufgabenstatus) |
| **Text-Dateien** | Fortschrittsnotizen, allgemeiner Kontext |
| **Git** | Änderungsverfolgung, Checkpoints |

### Multi-Context-Window Workflows

1. **Erstes Window**: Framework aufsetzen (Tests, Setup-Skripte)
2. **Folgende Windows**: An Todo-Liste iterieren
3. **Memory Tools nutzen**: State vor Context-Refresh speichern

```xml
<<context_management>>
Dein Context Window wird automatisch komprimiert, wenn es sich dem Limit nähert.
Stoppe Aufgaben nicht vorzeitig wegen Token-Budget-Bedenken.
Speichere deinen aktuellen Fortschritt und State in den Speicher bevor das Context Window refresht.
Sei so persistent und autonom wie möglich.
<</context_management>>
```

> "Claude 4.5 Modelle glänzen bei Long-Horizon Reasoning-Aufgaben mit außergewöhnlichen State-Tracking-Fähigkeiten."
> 
> — *Anthropic Claude 4 Best Practices (übersetzt)*[^1]

---

## Parallele Tool-Aufrufe

Claude 4.5 Modelle führen aggressiv Tools parallel aus. Das ist steuerbar:

### Parallele Ausführung maximieren

```xml
<<use_parallel_tool_calls>>
Wenn du vorhast, mehrere Tools aufzurufen und es keine Abhängigkeiten zwischen
den Tool-Calls gibt, mache alle unabhängigen Tool-Calls parallel.

Maximiere die Nutzung paralleler Tool-Calls wo möglich, um Geschwindigkeit
und Effizienz zu steigern.

Wenn jedoch einige Tool-Calls von vorherigen Calls abhängen, rufe diese Tools
NICHT parallel auf, sondern sequentiell.
<</use_parallel_tool_calls>>
```

### Parallele Ausführung reduzieren

```
Führe Operationen sequentiell mit kurzen Pausen zwischen jedem Schritt aus, um Stabilität zu gewährleisten.
```

> "Sonnet 4.5 ist besonders aggressiv darin, mehrere Operationen gleichzeitig abzufeuern."
> 
> — *Anthropic Claude 4 Best Practices (übersetzt)*[^1]

---

## Output-Formatierung kontrollieren

### Markdown und Aufzählungszeichen reduzieren

```xml
<<avoid_excessive_markdown_and_bullet_points>>
Beim Schreiben von Berichten, Dokumenten, technischen Erklärungen, Analysen
oder anderen Langform-Inhalten schreibe in klarer, fließender Prosa mit
vollständigen Absätzen.

Nutze Standard-Absatzumbrüche für Organisation und reserviere Markdown
primär für `inline code`, Code-Blöcke und einfache Überschriften.

Nutze KEINE geordneten oder ungeordneten Listen außer wenn:
a) wirklich diskrete Items präsentiert werden, wo Listenformat am besten ist
b) der User explizit eine Liste anfordert

Statt Items mit Aufzählungszeichen oder Nummern aufzulisten, integriere sie
natürlich in Sätze.
<</avoid_excessive_markdown_and_bullet_points>>
```

### Schlüsselprinzipien

1. **Sage Claude was zu tun ist** statt was nicht zu tun ist
2. **Nutze XML Format-Indikatoren**: "Schreibe in `<<prose_paragraphs>>` Tags"
3. **Passe Prompt-Stil an gewünschten Output an**

---

## Multishot Prompting (Beispiele)

Few-Shot Beispiele verbessern dramatisch die Output-Qualität.

> "Wenn du Claude Beispiele gibst, wie es Probleme durchdenken soll, wird es ähnlichen Reasoning-Patterns folgen."
> 
> — *Anthropic Extended Thinking Tips (übersetzt)*[^6]

### Beispiel: Klassifizierungsaufgabe

```xml
<instructions>
Klassifiziere Kundenfeedback als Positiv, Negativ oder Neutral.
</instructions>

<examples>
<example>
<input>Das Produkt kam schnell an und funktioniert super!</input>
<output>Positiv</output>
</example>

<example>
<input>Es ist okay, nichts Besonderes.</input>
<output>Neutral</output>
</example>

<example>
<input>Nach zwei Tagen kaputt. Geldverschwendung.</input>
<output>Negativ</output>
</example>
</examples>

<task>
Klassifiziere: "Gute Qualität aber Versand dauerte ewig."
</task>
```

### Best Practices

- Füge 3-5 diverse Beispiele ein
- Decke Edge Cases ab
- Passe Komplexität an deine tatsächliche Aufgabe an

---

## Code-Exploration und Halluzinations-Prävention

### Code-Exploration fördern

Opus 4.5 kann konservativ beim Erkunden von Code sein. Füge explizite Anweisungen hinzu:

```xml
<<investigate_before_answering>>
Lies und verstehe IMMER relevante Dateien, bevor du Code-Änderungen vorschlägst.
Spekuliere nicht über Code, den du nicht inspiziert hast.

Wenn der User eine spezifische Datei/Pfad referenziert, MUSST du sie öffnen
und inspizieren, bevor du erklärst oder Fixes vorschlägst.

Sei rigoros und persistent beim Durchsuchen von Code nach Schlüsselfakten.
<</investigate_before_answering>>
```

### Halluzinationen minimieren

```xml
<<grounded_answers>>
Spekuliere niemals über Code, den du nicht geöffnet hast.
Wenn der User eine spezifische Datei referenziert, MUSST du die Datei lesen, bevor du antwortest.

Stelle sicher, dass du relevante Dateien untersuchst und liest BEVOR du
Fragen beantwortest. Gib fundierte und halluzinationsfreie Antworten.
<</grounded_answers>>
```

> "Claude 4.x Modelle sind weniger anfällig für Halluzinationen und geben genauere, fundierte, intelligentere Antworten basierend auf dem Code."
> 
> — *Anthropic Claude 4 Best Practices (übersetzt)*[^1]

---

## Praktische Empfehlungen

### 1. Starte einfach

> "Wir empfehlen, die einfachste mögliche Lösung zu finden und Komplexität nur zu erhöhen, wenn nötig."
> 
> — *Anthropic Building Effective Agents (übersetzt)*[^7]

### 2. Nutze das richtige Modell

- **Opus 4.5**: Komplexe, mehrstufige Aufgaben
- **Sonnet 4.5**: Tägliche Arbeit, ausgewogene Performance
- **Haiku 4.5**: Hohes Volumen, schnelle Antworten

### 3. Fixiere Modellversionen

```python
model="claude-opus-4-5-20251101"  # Spezifischer Snapshot
model="claude-opus-4-5"           # Kann sich ändern
```

### 4. Teste mit echten Daten

Baue Evaluationen früh auf. Warte nicht bis zur Produktion.

### 5. Iteriere an Prompts

Lies Claudes Output, identifiziere Probleme, verfeinere Prompts. Das ist ein iterativer Prozess.

---

## Referenzen

[^1]: Anthropic. "Prompting Best Practices." *Anthropic Documentation*, Januar 2026. https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices

[^2]: Anthropic. "Introducing Claude Opus 4.5." *Anthropic News*, November 2025. https://www.anthropic.com/news/claude-opus-4-5

[^3]: Anthropic. "Use XML Tags to Structure Your Prompts." *Anthropic Documentation*, Januar 2026. https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/use-xml-tags

[^4]: Anthropic. "Giving Claude a Role with a System Prompt." *Anthropic Documentation*, Januar 2026. https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/system-prompts

[^5]: Anthropic. "Let Claude Think (Chain of Thought Prompting)." *Anthropic Documentation*, Januar 2026. https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/chain-of-thought

[^6]: Anthropic. "Extended Thinking Tips." *Anthropic Documentation*, Januar 2026. https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/extended-thinking-tips

[^7]: Anthropic. "Building Effective Agents." *Anthropic Engineering Blog*, Dezember 2024. https://www.anthropic.com/engineering/building-effective-agents

---

*Fragen? Kontaktiere mich auf [cursorconsulting.org](https://cursorconsulting.org)*
