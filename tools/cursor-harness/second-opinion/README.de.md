# second-opinion

Eine Cursor-Tool-Datei, die jeder Code-Änderung eine zweite Meinung verschafft. Das Chat-Modell in Cursor orchestriert; Opus 5.5 in der Claude-Code-CLI plant und setzt um; Codex in der Codex-CLI prüft jeden Plan, jeden Schritt und jeden PR, nur lesend. Keiner der beiden sieht die Überlegungen des anderen, nur Dateien, und jede Frage zum Produktverhalten geht an dich.

[English version](README.md)

Inspiriert von [cppalliance/tools-public](https://github.com/cppalliance/tools-public) (CC0, Stand `e0f98e97`: Form der Tool-Datei, Plan-Vertrag, Transport-Commits, Prompt-Regelwerk) und [microsoft/waza](https://github.com/microsoft/waza) (MIT, Stand `1234308b`: golden-Sperren, Bewertung von Tool-Aufrufen, adversariale Kanarienwörter). Nur Ideen, kein Code und kein Text kopiert.

## Was es tut

| Modus | Du gibst | Du bekommst |
|---|---|---|
| develop (Standard) | eine Aufgabe | einen geprüften Plan, eine Freigabe im Plan-Modus von Cursor für deine Entscheidungen, dann pro Schritt einen Commit `[WIP] Step <n>`, jeder von Codex geprüft und von Opus beurteilt |
| review | einen PR oder Branch | ein Opus-Review, ein blindes Codex-Review und eine Triage; nichts wird geändert |
| sweep | ein Modul | beide Prüfer lesen jede Datei vollständig; Abdeckung aus den Logs; eine Triage |

Uneinigkeit zwischen den Modellen entscheidet ein Schiedsrichter-Test pro Befund, oder du. Nichts wird gepusht; Push, Squash und Merge bleiben bei dir.

## Installation

Prüfe zuerst [PREREQUISITES.md](PREREQUISITES.md). Getestet ist nur Windows mit PowerShell.

**a) Klonen und erwähnen (ohne Einrichtung).** Klone dieses Repo. Öffne dein Ziel-Repo in Cursor, füge den Ordner des Klons dem Workspace hinzu (Multi-Root) und schreibe im Agent-Chat:

```text
@second-opinion.md develop: <deine Aufgabe>
```

Statt der Erwähnung geht auch der absolute Pfad der Datei. Cursor beschreibt @-Erwähnungen von Dateien unter [cursor.com/docs/context/mentions](https://cursor.com/docs/context/mentions).

**b) Optionaler Benutzer-Skill (nur Verweis).** Lege `~/.cursor/skills/second-opinion/SKILL.md` an:

```markdown
---
name: second-opinion
description: Second opinion on code changes with Opus and Codex. Use only when invoked.
disable-model-invocation: true
---

Read <absoluter Pfad deines Klons>/tools/cursor-harness/second-opinion/second-opinion.md in full and follow it.
```

Dann im Agent-Chat `/second-opinion` tippen. Der Skill zeigt nur auf die geklonte Datei, `git pull` im Klon aktualisiert ihn also. Benutzer-Skills in `~/.cursor/skills/` und `disable-model-invocation` beschreibt [cursor.com/docs/context/skills](https://cursor.com/docs/context/skills).

Eine Command-Datei wird nicht mitgeliefert.

## Erster Lauf

1. `python -B tools/cursor-harness/second-opinion/scripts/doctor.py` (im Klon). Jede Zeile `ok`, Exit 0. Es meldet, ob und wie du angemeldet bist, nie als wer.
2. Im Ziel-Repo mit einer kleinen Aufgabe beginnen. Der Run-Ordner entsteht unter `.second-opinion/runs/` im Ziel-Repo; das Tool trägt `/.second-opinion/` in `.git/info/exclude` ein, `git status` bleibt also sauber und keine versionierte Datei ändert sich.

## Repo-Regeln für Opus: CLAUDE.local.md

Opus in der Claude-Code-CLI liest `CLAUDE.md` und `CLAUDE.local.md`; `AGENTS.md` liest es von selbst nur, wenn keine der beiden existiert. Willst du in einem Repo, das auf `AGENTS.md` setzt, eigene Notizen für Opus, lege `CLAUDE.local.md` im Repo-Wurzelordner an, mit dem Import zuerst:

```markdown
@AGENTS.md

<deine Notizen>
```

und schließe sie lokal aus, ohne die `.gitignore` des Repos anzufassen:

```powershell
Add-Content (Join-Path (git rev-parse --git-common-dir) "info/exclude") "CLAUDE.local.md"
```

Quelle: [Claude-Code-Doku zu Memory](https://code.claude.com/docs/en/memory): `CLAUDE.local.md` zählt als CLAUDE.md und verhindert standardmäßig, dass `AGENTS.md` geladen wird; `@path`-Importe laden die Datei (relative oder absolute Pfade, höchstens vier Stufen); Importe außerhalb des Arbeitsverzeichnisses brauchen eine einmalige Freigabe. Die Doku empfiehlt `.gitignore`; `.git/info/exclude` wirkt gleich, ohne versionierte Änderung. Ebenfalls dort: eine unversionierte `CLAUDE.local.md` gibt es nur im Checkout, in dem du sie angelegt hast, und second-opinion startet die CLIs in eigenen Worktrees. second-opinion liest diese Dateien als Repo-Regeln und ändert sie nie.

## Dateien

- `second-opinion.md`: die Tool-Datei. Die einzige Datei, die du erwähnst.
- `scripts/`: Runner für beide CLIs, Watchdog, `make_prompt.py` (kopiert Prompt-Blöcke wortgetreu), `doctor.py`, `grade_run.py`, `skill_check.py`, Review-Schema, gesperrte Begriffe.
- `evals/`: sechs Regressionsaufgaben, Saat-Fehler, golden- und Qualitätserwartungen, vier adversariale Varianten, die erste Basis. Den geprüften Modellen nie gezeigt.
- `PREREQUISITES.md`, `DEPENDENCIES.md`, `CHANGELOG.md`.

## Grenzen

- Nur Windows mit PowerShell; für macOS und Linux wird nichts behauptet.
- Die develop-Freigabe braucht den Plan-Modus von Cursor.
- Beide CLIs rechnen über deine eigenen Abos oder Schlüssel ab; das Tool notiert Codex-Tokens, rechnet aber keine Kosten aus.
- Dateien außerhalb des Repos: Die CLIs führen eigene Aufzeichnungen. Opus kann im Plan-Modus eine Plandatei unter `~/.claude/plans/` schreiben; die Claude-CLI legt Sitzungsprotokolle unter `~/.claude` ab, die Codex-CLI unter `~/.codex/sessions`. Das Tool fasst beides nie an; wer keine Reste will, entfernt sie selbst.
- Aufgaben 1 bis 4 der Evals brauchen einen Menschen an der Freigabe und sind nicht Teil der automatischen Abnahme.
