# Dependencies

Read this file before changing anything in the Foreman folder. Paths are relative to this file. Run `python -B skill_check.py` after every change; a change counts only when it is green.

| If this changes | these must follow |
|---|---|
| a heading in `../foreman.md` | every `section "..."` reference to it in `../foreman.md`; `skill_check.py` checks |
| a block tag (mode, sub-agent, prompt or schema) | the tag names used in `../foreman.md` (Start, Sub-agent dispatch, the mode blocks), the tag check in `skill_check.py`; for the schema tag also `$SchemaTag` in `../scripts/run.ps1` and `SCHEMA_TAG` in `grade_run.py` |
| a placeholder in a prompt block | every filling of that block described in the mode blocks of `../foreman.md` |
| the approved non-normative text | `../foreman.md` and the byte-equal check in `skill_check.py` together |
| a CLI switch, a deny pattern or a time limit | `../scripts/run.ps1`, section "Calling the CLIs" and the switch lists in the `prerequisites-instructions` block of `../foreman.md`, the `runner_denies` and golden lines in `evals/rules/` and `evals/expectations.md`, `CHANGELOG.md` |
| the stream format of a CLI | `grade_run.py` (`Stream`), the answer extraction in `../scripts/run.ps1`, the anchored model and token searches and the full-read patterns in the `coverage-instructions` block of `../foreman.md` |
| the `review-schema-instructions` block | the Codex prompt blocks, the schema extraction in `../scripts/run.ps1`, `json_artifacts` checks in `grade_run.py`, the triage rule |
| the `prerequisites-instructions` block | the Setup section of `../README.md` and `../README.de.md`, the `setup-mode-instructions` block |
| `../foreman.md` or any file in `../scripts/` | the version: `Version:` in `../foreman.md` and a new section in `CHANGELOG.md` |
| a prerequisite's minimum version | the `prerequisites-instructions` block, the evidence line in `CHANGELOG.md` |
| a file or path is renamed or removed | `../foreman.md`, `../README.md`, `../README.de.md`, `banned-terms.txt` if the old name must not return |
| the run folder layout | section "Run state" and the mode blocks of `../foreman.md`, `json_artifacts` and `markdown_artifacts` in `evals/rules/`, the run paths in `grade_run.py` |
| the off-limits rule for this folder | binding rule 1 in `../foreman.md`, `evals/README.md`, the tool-path check in section "Prompt assembly" of `../foreman.md` |
| the playground, a seed or a task | `evals/tasks.md`, `evals/seeded-bugs.md` (line numbers), `evals/rules/`, `evals/expectations.md`, `playground/` |
| the install paths or the Setup section | `../README.md` and `../README.de.md` together |
| the Foreman folder's place in this repo | the clone paths in `../README.md` and `../README.de.md`, `../../README.md`, `../../../README.md` and the repo's root `../../../../README.md`; the tool itself resolves its folder at run time |

Snapshots: `evals/baseline-*.md` are dated. They stay complete in themselves and change only through a dated addendum; a new series gets a new file.
