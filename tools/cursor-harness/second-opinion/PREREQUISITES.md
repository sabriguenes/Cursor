# Prerequisites

`scripts/doctor.py` reads the table below and runs exactly one check per row. A row without a check, or a check without a row, makes doctor fail. Change both together (see `DEPENDENCIES.md`).

Platform: only Windows with PowerShell is evidenced. Nothing is claimed for macOS or Linux.

"Minimum version" is the version the 2026-10-01 test series ran on, where it was recorded. "not recorded" means the series did not record one; doctor then checks presence only.

| id | Dependency | Minimum version | Needed for | Required | How to check |
|---|---|---|---|---|---|
| claude-cli | Claude Code CLI, installed through npm (`claude.exe` next to the npm shim) | not recorded | Opus: plan, steps, verdicts, reviews (`claude -p`) | required | `claude --version` |
| claude-login | Claude Code login with a Claude subscription | n/a | Opus runs on the subscription, not on an API key | required | `claude auth status --json`: logged in, method claude.ai |
| codex-cli | Codex CLI, installed through npm (`codex.js` next to the npm shim) | 0.159.1 | Codex: read-only reviews (`codex exec`) | required | `codex --version` |
| codex-login | Codex login (ChatGPT or API key) | n/a | Codex reviews | required | `codex login status` |
| codex-sandbox | Windows sandbox setting `sandbox = "unelevated"` under `[windows]` in `~/.codex/config.toml` | n/a | read-only Codex can read files on Windows; without it reads are "blocked by policy" | required | open the file; only the human edits it |
| codex-plugin | Codex plugin for Claude Code, `codex@openai-codex` | not recorded | optional plugin review (`/codex:review`) inside a Claude run | optional | `claude plugin list` |
| node | Node.js | not recorded | the Codex runner starts `codex.js` with node | required | `node --version` |
| git | Git | not recorded | worktrees, diffs, transport commits | required | `git --version` |
| python | Python | 3.11 (needed by doctor.py for tomllib, not from the series) | doctor.py, make_prompt.py, skill_check.py, grade_run.py | required | `python --version` |
| uv | uv | not recorded | Python repos that use uv, and the eval fixture | required | `uv --version` |
| powershell | Windows PowerShell (`powershell.exe`) | not recorded | runners and watchdog | required | `powershell.exe -NoProfile -Command $PSVersionTable.PSVersion` |
| gh | GitHub CLI, logged in | not recorded | review mode on a GitHub PR (fetching the PR) | optional | `gh --version`, `gh auth status` |
