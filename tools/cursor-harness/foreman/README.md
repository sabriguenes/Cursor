# The Foreman

A Cursor tool file that builds nothing itself. The chat model in Cursor orchestrates; Opus in the Claude Code CLI plans and implements; Codex in the Codex CLI reviews every plan, step and pull request read-only. Disagreements are settled by a test, every decision that is yours comes to you one at a time, and every run is recorded under `.foreman/runs/` in the target repo.

[Deutsche Version](README.de.md)

## What it does

| Mode | You give | You get |
|---|---|---|
| develop | a plan or a task | a reviewed plan, a gate for your decisions, then one `[WIP]` commit per step, each reviewed by Codex and judged by Opus |
| review | a pull request or branch | an Opus review, a blind Codex review and a triage; nothing changed |
| sweep | a module | both reviewers read every file in full, coverage is checked, then a triage |
| setup | nothing | a prerequisites check, then the pointer skill and the Windows sandbox line, each written only after your yes |

Nothing is pushed. Renaming, squashing, pushing and merging stay yours. To continue an interrupted run from a fresh chat, mention the file again and say resume.

## Install

Clone this repo. The tool file is `tools/cursor-harness/foreman/foreman.md` in the clone. Use it in one of two ways:

- **Mention it.** Open your target repo in Cursor, add the clone's folder to the workspace, and in agent chat type `@foreman.md` followed by a mode and its subject, for example `@foreman.md develop: <your plan or task>`. The file's absolute path works as well.
- **Pointer skill.** Create `~/.cursor/skills/foreman/SKILL.md` whose only content points to the cloned file, or let setup mode propose it:

```markdown
---
name: foreman
description: "Take a plan, have Opus build it step by step in the Claude Code CLI while Codex reviews every change read-only in the Codex CLI, settle disputes with tests, and bring the human every decision that is theirs; also reviews a pull request, sweeps a module, or sets up a machine once."
---
Read <absolute path of your clone>/tools/cursor-harness/foreman/foreman.md in full and follow it.
```

The skill only points, so `git pull` in the clone updates it.

Never copy the tool into a work repo. Opus and Codex must never see the tool folder; a copy inside the repo they work on would show it to them.

## Setup

Once per machine, in this order. Only Windows with PowerShell is tested.

1. Install the Claude Code CLI and log in with a Claude subscription. Choose Opus in Claude Code with `/model`.
   Check: `claude --version` prints a version; `claude auth status --text` shows that you are logged in and with which method; `/model` inside a Claude Code session shows the current choice.
2. Install the Codex CLI and log in. Two ways, neither required:
   - ChatGPT login: `codex login` opens the sign-in. It runs on your ChatGPT subscription and uses the plan's default model.
   - API key: billed per use, and needed for models your ChatGPT plan does not offer. Set a spending limit at the provider. Enter the key through Codex's own login: `codex login --with-api-key` reads it from standard input. Do not rely on the `OPENAI_API_KEY` environment variable: `run.ps1` removes it from every call.
   Check: `codex --version` prints a version; `codex login status` shows that you are logged in and with which method.
3. Optional: fix the Codex model with a `model =` line in the Codex config (`$env:CODEX_HOME/config.toml` when `CODEX_HOME` is set, otherwise `~/.codex/config.toml`). Without the entry, Codex uses your account's default model. The Foreman never sets a model and records the one used in `RUN.md`.
   Check: open the Codex config and look for the `model =` line; no line means the account default.
4. On Windows: `sandbox = "unelevated"` under `[windows]` in the Codex config (`$env:CODEX_HOME/config.toml` when `CODEX_HOME` is set, otherwise `~/.codex/config.toml`). Without it, read-only Codex is blocked even from plain file reads.
   Check: open the Codex config and find `sandbox = "unelevated"` in the `[windows]` section.
5. Clone this repo, mention `foreman.md` in agent chat and say "setup". The Foreman checks every prerequisite, names the fix for each missing one, proposes the pointer skill and, on Windows, the sandbox line, and writes each only after your yes. Logins, keys, installations and the model choice stay yours.
   Check: the Foreman reports `ready`.

## Files

- `foreman.md`: the tool file. The only file you mention.
- `scripts/run.ps1`: starts the Claude Code CLI or the Codex CLI inside the worktree, with the watchdog; `-Cli selftest` tests the watchdog without a CLI.
- `maintainers/`: checks, evals, the playground repo template, [CHANGELOG.md](maintainers/CHANGELOG.md) and [DEPENDENCIES.md](maintainers/DEPENDENCIES.md). Only maintainers need it; the models never see it.

## Limits

- Windows with PowerShell only; nothing is claimed for macOS or Linux.
- Both CLIs bill against your own subscriptions or keys. The Foreman records model and tokens per call and computes no cost.
- The watchdog (900 s without output, 3600 s in total) is proven only by its self-test. No real CLI stall has happened yet, so its behavior on one is untested.
- Sweep is evidenced only on a module of three files. Larger modules are untested.
- Files outside the repo: Opus in plan mode may leave a notes file under `~/.claude/plans/`. The Claude CLI keeps session logs under `~/.claude`, the Codex CLI under `~/.codex/sessions`. The Foreman never touches them; remove them yourself if you want no traces.

---

[Back to Cursor Harness](../README.md) | [Back to Tools & Resources](../../README.md) | [Back to main README](../../../README.md)
