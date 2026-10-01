# Dependencies

Read this file before changing anything in the tool folder. Run `python -B scripts/skill_check.py` after every change; a change counts only when it is green.

| If this changes | these must follow |
|---|---|
| a heading in `second-opinion.md` | every `section "..."` reference to it in `second-opinion.md`; `skill_check.py` checks |
| a block tag (mode or prompt) | `BLOCK_TAGS` in `scripts/skill_check.py`, the mode or prompt names used in `second-opinion.md` |
| a placeholder in a prompt block | every `make_prompt.py` call described in the mode blocks |
| a CLI switch, a deny pattern or a time limit | `scripts/runner-claude.ps1` or `scripts/runner-codex.ps1`, `scripts/invoke-cli.ps1`, `scripts/watchdog.ps1`, the `runner_denies` and golden lines in `evals/rules/` and `evals/expectations.md`, `CHANGELOG.md` |
| the stream format of a CLI | `scripts/grade_run.py` (`Stream`), the answer extraction in `scripts/runner-claude.ps1` |
| `scripts/review.schema.json` | the Codex prompt blocks, `json_artifacts` checks in `scripts/grade_run.py`, the triage rule |
| any file in `scripts/` | the version: `Version:` in `second-opinion.md` and a new section in `CHANGELOG.md` |
| a row of `PREREQUISITES.md` | the matching entry in `CHECKS` of `scripts/doctor.py`, and the reverse; doctor fails on any mismatch |
| a prerequisite's minimum version | `PREREQUISITES.md`, the evidence line in `CHANGELOG.md` |
| a file or path is renamed or removed | `second-opinion.md`, `README.md`, `README.de.md`, `scripts/banned-terms.txt` if the old name must not return |
| the run folder layout | the Run state and mode blocks of `second-opinion.md`, `json_artifacts` and `markdown_artifacts` in `evals/rules/` |
| the off-limits rule for `evals/` | binding rule 1 in `second-opinion.md`, `evals/README.md`, the leak check in `scripts/make_prompt.py` |
| the eval template, a seed or a task | `evals/tasks.md`, `evals/seeded-bugs.md` (line numbers), `evals/rules/`, `evals/expectations.md` |
| the install paths | `README.md` and `README.de.md` together |
| the tool folder's place in this repo | the clone paths in `README.md` and `README.de.md` (skill pointer, doctor command), the parent `../README.md`, `tools/README.md` and the repo's root `README.md`; the tool itself resolves its folder at run time |

Snapshots: `evals/baseline-*.md` are dated. They stay complete in themselves and change only through a dated addendum; a new series gets a new file.
