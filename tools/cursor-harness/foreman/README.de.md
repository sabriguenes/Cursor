# The Foreman

Eine Cursor-Tool-Datei, die selbst nichts baut. Das Chat-Modell in Cursor orchestriert; Opus in der Claude-Code-CLI plant und setzt um; Codex in der Codex-CLI prüft jeden Plan, jeden Schritt und jeden Pull Request, nur lesend. Uneinigkeit entscheidet ein Test, jede Entscheidung, die deine ist, kommt einzeln zu dir, und jeder Lauf wird unter `.foreman/runs/` im Ziel-Repo festgehalten.

[English version](README.md)

## Was es tut

| Modus | Du gibst | Du bekommst |
|---|---|---|
| develop | einen Plan oder eine Aufgabe | einen geprüften Plan, eine Freigabe für deine Entscheidungen, dann pro Schritt einen `[WIP]`-Commit, jeder von Codex geprüft und von Opus beurteilt |
| review | einen Pull Request oder Branch | ein Opus-Review, ein blindes Codex-Review und eine Triage; nichts wird geändert |
| sweep | ein Modul | beide Prüfer lesen jede Datei vollständig, die Abdeckung wird geprüft, dann eine Triage |
| setup | nichts | eine Prüfung der Voraussetzungen, dann der Verweis-Skill und die Windows-Sandbox-Zeile, jeweils erst nach deinem Ja geschrieben |

Nichts wird gepusht. Umbenennen, Squash, Push und Merge bleiben bei dir. Um einen unterbrochenen Lauf in einem neuen Chat fortzusetzen, erwähne die Datei erneut und sag resume.

## Installation

Klone dieses Repo. Die Tool-Datei liegt im Klon unter `tools/cursor-harness/foreman/foreman.md`. Nutze sie auf einem von zwei Wegen:

- **Erwähnen.** Öffne dein Ziel-Repo in Cursor, füge den Ordner des Klons dem Workspace hinzu und schreibe im Agent-Chat `@foreman.md`, gefolgt von einem Modus und seinem Gegenstand, zum Beispiel `@foreman.md develop: <dein Plan oder deine Aufgabe>`. Der absolute Pfad der Datei geht ebenso.
- **Verweis-Skill.** Lege `~/.cursor/skills/foreman/SKILL.md` an, deren einziger Inhalt auf die geklonte Datei zeigt, oder lass ihn vom setup-Modus vorschlagen:

```markdown
---
name: foreman
description: "Take a plan, have Opus build it step by step in the Claude Code CLI while Codex reviews every change read-only in the Codex CLI, settle disputes with tests, and bring the human every decision that is theirs; also reviews a pull request, sweeps a module, or sets up a machine once."
---
Read <absoluter Pfad deines Klons>/tools/cursor-harness/foreman/foreman.md in full and follow it.
```

Der Skill zeigt nur auf die Datei, `git pull` im Klon aktualisiert ihn also.

Kopiere das Tool nie in ein Arbeits-Repo. Opus und Codex dürfen den Tool-Ordner nie sehen; eine Kopie im Repo, an dem sie arbeiten, würde ihn ihnen zeigen.

## Setup

Einmal pro Rechner, in dieser Reihenfolge. Getestet ist nur Windows mit PowerShell.

1. Installiere die Claude-Code-CLI und melde dich mit einem Claude-Abo an. Wähle Opus in Claude Code mit `/model`.
   Prüfen: `claude --version` gibt eine Version aus; `claude auth status --text` zeigt, dass du angemeldet bist und mit welcher Methode; `/model` in einer Claude-Code-Sitzung zeigt die aktuelle Wahl.
2. Installiere die Codex-CLI und melde dich an. Zwei Wege, keiner ist Pflicht:
   - ChatGPT-Anmeldung: `codex login` öffnet die Anmeldung. Sie läuft über dein ChatGPT-Abo und nutzt das Standardmodell des Plans.
   - API-Schlüssel: wird pro Nutzung abgerechnet und ist nötig für Modelle, die dein ChatGPT-Plan nicht anbietet. Setze beim Anbieter ein Ausgabenlimit. Gib den Schlüssel über Codex' eigene Anmeldung ein: `codex login --with-api-key` liest ihn von der Standardeingabe. Verlass dich nicht auf die Umgebungsvariable `OPENAI_API_KEY`: `run.ps1` entfernt sie vor jedem Aufruf.
   Prüfen: `codex --version` gibt eine Version aus; `codex login status` zeigt, dass du angemeldet bist und mit welcher Methode.
3. Optional: lege das Codex-Modell mit einer Zeile `model =` in der Codex-Konfiguration fest (`$env:CODEX_HOME/config.toml`, wenn `CODEX_HOME` gesetzt ist, sonst `~/.codex/config.toml`). Ohne den Eintrag nutzt Codex das Standardmodell deines Kontos. Der Foreman setzt nie ein Modell und notiert das verwendete in `RUN.md`.
   Prüfen: öffne die Codex-Konfiguration und suche die Zeile `model =`; keine Zeile heißt Kontostandard.
4. Unter Windows: `sandbox = "unelevated"` unter `[windows]` in der Codex-Konfiguration (`$env:CODEX_HOME/config.toml`, wenn `CODEX_HOME` gesetzt ist, sonst `~/.codex/config.toml`). Ohne die Zeile wird Codex im Nur-Lese-Modus sogar beim einfachen Lesen von Dateien blockiert.
   Prüfen: öffne die Codex-Konfiguration und finde `sandbox = "unelevated"` im Abschnitt `[windows]`.
5. Klone dieses Repo, erwähne `foreman.md` im Agent-Chat und sag "setup". Der Foreman prüft jede Voraussetzung, nennt für jede fehlende die Abhilfe, schlägt den Verweis-Skill und unter Windows die Sandbox-Zeile vor und schreibt beides jeweils erst nach deinem Ja. Anmeldungen, Schlüssel, Installationen und die Modellwahl bleiben bei dir.
   Prüfen: der Foreman meldet `ready`.

## Dateien

- `foreman.md`: die Tool-Datei. Die einzige Datei, die du erwähnst.
- `scripts/run.ps1`: startet die Claude-Code-CLI oder die Codex-CLI im Worktree, mit Watchdog; `-Cli selftest` prüft den Watchdog ohne CLI.
- `maintainers/`: Prüfungen, Evals, die Playground-Repo-Vorlage, [CHANGELOG.md](maintainers/CHANGELOG.md) und [DEPENDENCIES.md](maintainers/DEPENDENCIES.md). Nur für Maintainer; die Modelle sehen den Ordner nie.

## Grenzen

- Nur Windows mit PowerShell; für macOS und Linux wird nichts behauptet.
- Beide CLIs rechnen über deine eigenen Abos oder Schlüssel ab. Der Foreman notiert Modell und Tokens pro Aufruf und rechnet keine Kosten aus.
- Der Watchdog (900 s ohne Ausgabe, 3600 s insgesamt) ist nur durch seinen Selbsttest belegt. Ein echter Hänger einer CLI kam noch nicht vor, sein Verhalten dabei ist also ungeprüft.
- Sweep ist nur an einem Modul mit drei Dateien belegt. Größere Module sind ungeprüft.
- Dateien außerhalb des Repos: Opus kann im Plan-Modus eine Notizdatei unter `~/.claude/plans/` hinterlassen. Die Claude-CLI legt Sitzungsprotokolle unter `~/.claude` ab, die Codex-CLI unter `~/.codex/sessions`. Der Foreman fasst sie nie an; wer keine Reste will, entfernt sie selbst.

---

[Zurück zu Cursor Harness](../README.md) | [Zurück zu Tools & Resources](../../README.md) | [Zurück zur Haupt-README](../../../README.md)
