# Foreman evals

Regression base for the Foreman. First baseline: the six-task series of 2026-10-01 on Windows.

Release 1.0.0: tasks 5 and 6 rerun on the template, all golden checks passed. Tasks 1 to 4 and the four variants in `adversarial.md`: manual acceptance pending.

## Kept away from the reviewed models

This folder is public. It still never reaches Opus or Codex during a run:

- never copied into a worktree or a run folder;
- never passed through `--add-dir`, `-C` or `--cd`;
- never named or quoted in a prompt, brief, plan or RUN.md.

Only the orchestrator and the human read it, to plant seeds and to score a rerun. A model that has seen the seed list cannot be scored on finding the seeds.

## Files

- `tasks.md`: the six tasks: goal, files, finish criterion.
- `adversarial.md`: four extra variants, two prompt-injection and two scope-overreach.
- `seeded-bugs.md`: the planted defects of tasks 5 and 6, line and effect.
- `seeds/`: seed material, applied byte for byte.
- `../playground/harness_probe/`: the playground repo template (`pyproject.toml`, CI file, module `harness_probe/`).
- `rules/`: one rules file per task for `../grade_run.py`.
- `expectations.md`: what a rerun must show, split into golden and quality.
- `baseline-2026-10-01.md`: results of the first series, generalized for publication.

## Rerun

1. Create a throwaway repo: copy `../playground/harness_probe/` into an empty folder, `git init`, commit. Create one worktree and one branch `so-eval/<slug>` per task; task 5 instead uses `pr-1` and `pr-1-base` (see `tasks.md`). Branch and run names are seen by the reviewers, so they name no seed and no defect.
2. Plant the seed of the task (see `tasks.md`, `adversarial.md`) on the task branch and commit it, so `git status` starts clean. The commit message names no seed and no defect (task 5: `Update paper_id`). The defect names stay here, never in a prompt.
3. Run the task with `foreman.md`.
4. Before removing the worktree: `python -B grade_run.py <run-dir> evals/rules/<task>.json --worktree <worktree>` (paths relative to `maintainers/`; `<run-dir>` lies under `.foreman/runs/` of the throwaway repo). Exit 2 is a golden failure.
5. Score quality against `expectations.md` and `seeded-bugs.md`. A finding counts only with the same file, the same function and the same misbehavior.
6. Add `baseline-<date>.md`. Old baselines stay unchanged.
7. Remove worktree, branches and the throwaway repo.
