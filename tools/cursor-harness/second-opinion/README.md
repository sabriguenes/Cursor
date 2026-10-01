# second-opinion

A Cursor tool file that gets every code change a second opinion. The chat model in Cursor orchestrates; Opus 5.5 in the Claude Code CLI plans and implements; Codex in the Codex CLI reviews every plan, step and PR read-only. Neither reviewer sees the other's reasoning, only files, and every question about product behavior goes to you.

[Deutsche Version](README.de.md)

Inspired by [cppalliance/tools-public](https://github.com/cppalliance/tools-public) (CC0, at `e0f98e97`: tool-file form, plan contract, transport commits, prompt rulebook) and [microsoft/waza](https://github.com/microsoft/waza) (MIT, at `1234308b`: golden gates, tool-constraint grading, adversarial canaries). Ideas only; no code or text copied.

## What it does

| Mode | You give | You get |
|---|---|---|
| develop (default) | a task | a reviewed plan, a gate in Cursor plan mode for your decisions, then one `[WIP] Step <n>` commit per step, each reviewed by Codex and judged by Opus |
| review | a PR or branch | an Opus review, a blind Codex review, and a triage; nothing changed |
| sweep | a module | both reviewers read every file in full; coverage from the logs; a triage |

Disagreements between the models are settled by one referee test per finding, or by you. Nothing is pushed; push, squash and merge stay yours.

## Install

Check [PREREQUISITES.md](PREREQUISITES.md) first. Only Windows with PowerShell is tested.

**a) Clone and mention (no setup).** Clone this repo. Open your target repo in Cursor and add the clone's folder to the workspace (multi-root), then type in Agent chat:

```text
@second-opinion.md develop: <your task>
```

You can also give the file's absolute path instead of the mention. Cursor documents @-mentions of files at [cursor.com/docs/context/mentions](https://cursor.com/docs/context/mentions).

**b) Optional user skill (pointer only).** Create `~/.cursor/skills/second-opinion/SKILL.md` with:

```markdown
---
name: second-opinion
description: Second opinion on code changes with Opus and Codex. Use only when invoked.
disable-model-invocation: true
---

Read <absolute path of your clone>/tools/cursor-harness/second-opinion/second-opinion.md in full and follow it.
```

Then type `/second-opinion` in Agent chat. The skill only points at the cloned file, so `git pull` in the clone updates it. User-level skills in `~/.cursor/skills/` and `disable-model-invocation` are documented at [cursor.com/docs/context/skills](https://cursor.com/docs/context/skills).

No command file is shipped.

## First run

1. `python -B tools/cursor-harness/second-opinion/scripts/doctor.py` (from the clone). Every line `ok`, exit 0. It prints whether you are logged in and how, never who.
2. In the target repo, start with a small task. The run folder appears under `.second-opinion/runs/` in the target repo; the tool adds `/.second-opinion/` to `.git/info/exclude`, so `git status` stays clean and no tracked file changes.

## Repo rules for Opus: CLAUDE.local.md

Opus in the Claude Code CLI reads `CLAUDE.md` and `CLAUDE.local.md`; it reads `AGENTS.md` on its own only when neither exists. If you want personal notes for Opus in a repo that relies on `AGENTS.md`, create `CLAUDE.local.md` at the repo root with an import first:

```markdown
@AGENTS.md

<your notes>
```

and exclude it locally, without touching the repo's `.gitignore`:

```powershell
Add-Content (Join-Path (git rev-parse --git-common-dir) "info/exclude") "CLAUDE.local.md"
```

Source: [Claude Code memory docs](https://code.claude.com/docs/en/memory): `CLAUDE.local.md` counts as a CLAUDE.md and stops `AGENTS.md` from loading by default; `@path` imports load the file (relative or absolute paths, at most four hops); imports outside the working directory need a one-time approval. The docs suggest `.gitignore`; `.git/info/exclude` has the same effect without a tracked change. Note from the same page: an untracked `CLAUDE.local.md` exists only in the checkout where you created it, and second-opinion runs the CLIs in separate worktrees. second-opinion reads these files as repo rules and never edits them.

## Files

- `second-opinion.md`: the tool file. The only file you mention.
- `scripts/`: runners for both CLIs, watchdog, `make_prompt.py` (copies prompt blocks word for word), `doctor.py`, `grade_run.py`, `skill_check.py`, review schema, banned terms.
- `evals/`: six regression tasks, seeds, golden and quality expectations, four adversarial variants, the first baseline. Never shown to the reviewed models.
- `PREREQUISITES.md`, `DEPENDENCIES.md`, `CHANGELOG.md`.

## Limits

- Windows with PowerShell only; nothing is claimed for macOS or Linux.
- The develop gate needs Cursor's plan mode.
- Both CLIs bill against your own subscriptions or keys; the tool records Codex tokens but computes no cost.
- Files outside the repo: the CLIs keep their own records. Opus in plan mode may write a plan file under `~/.claude/plans/`; the Claude CLI keeps session logs under `~/.claude`, the Codex CLI under `~/.codex/sessions`. The tool never touches either; remove them yourself if you want no traces.
- Tasks 1 to 4 of the evals need a human at the gate and are not part of the automated acceptance.
