# SPDX-License-Identifier: MIT
"""Read-only environment check for second-opinion.

Usage: python -B doctor.py
Reads the table in PREREQUISITES.md (one folder up) and runs one check per row.
Changes nothing. Prints one line per row; a missing row carries its remedy.
Never prints e-mail addresses, account or organization names, or tokens:
login rows print only "logged in: yes|no" and the kind (subscription or API key).

Exit 0 when every required row is ok, 1 otherwise.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent.parent
PREREQUISITES = TOOL_DIR / "PREREQUISITES.md"
TIMEOUT_SEC = 60
CODEX_MIN = (0, 159, 1)
PYTHON_MIN = (3, 11)
CLAUDE_EXE = Path("node_modules") / "@anthropic-ai" / "claude-code" / "bin" / "claude.exe"
CODEX_JS = Path("node_modules") / "@openai" / "codex" / "bin" / "codex.js"
SECRET_ENV = ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "OPENAI_API_KEY")


def run(args: list[str]) -> tuple[int, str]:
    """Run a command with API-key variables removed from the child env; output stays in memory."""
    exe = shutil.which(args[0])
    if exe is None:
        return 127, ""
    env = {k: v for k, v in os.environ.items() if k not in SECRET_ENV}
    try:
        proc = subprocess.run([exe, *args[1:]], capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=TIMEOUT_SEC, env=env)
    except (OSError, subprocess.TimeoutExpired):
        return 126, ""
    return proc.returncode, proc.stdout + proc.stderr


def version_of(text: str) -> tuple[int, ...] | None:
    m = re.search(r"(\d+)\.(\d+)\.(\d+)", text)
    return tuple(int(g) for g in m.groups()) if m else None


def shim_sibling(command: str, relative: Path) -> bool:
    shim = shutil.which(command)
    return shim is not None and (Path(shim).parent / relative).exists()


def check_claude_cli() -> tuple[bool, str]:
    code, out = run(["claude", "--version"])
    if code != 0:
        return False, "install Claude Code through npm, then reopen the shell"
    if not shim_sibling("claude", CLAUDE_EXE):
        return False, "claude.exe not found next to the npm shim; reinstall Claude Code through npm"
    return True, f"version {'.'.join(map(str, version_of(out) or ()))}"


def check_claude_login() -> tuple[bool, str]:
    code, out = run(["claude", "auth", "status", "--json"])
    try:
        data = json.loads(out)
    except ValueError:
        return False, "logged in: no; run `claude auth login` with your Claude subscription"
    logged_in = data.get("loggedIn") is True
    kind = "subscription" if data.get("authMethod") == "claude.ai" else "API key or other"
    if not logged_in:
        return False, "logged in: no; run `claude auth login` with your Claude subscription"
    if kind != "subscription":
        return False, f"logged in: yes, kind: {kind}; log in with a Claude subscription (`claude auth login`)"
    return True, f"logged in: yes, kind: {kind}"


def check_codex_cli() -> tuple[bool, str]:
    code, out = run(["codex", "--version"])
    found = version_of(out)
    if code != 0 or found is None:
        return False, "install the Codex CLI through npm, then reopen the shell"
    if not shim_sibling("codex", CODEX_JS):
        return False, "codex.js not found next to the npm shim; reinstall the Codex CLI through npm"
    shown = ".".join(map(str, found))
    if found < CODEX_MIN:
        return False, f"version {shown} is below {'.'.join(map(str, CODEX_MIN))}; update the Codex CLI"
    return True, f"version {shown}"


def check_codex_login() -> tuple[bool, str]:
    code, out = run(["codex", "login", "status"])
    if code != 0 or "not logged in" in out.lower():
        return False, "logged in: no; run `codex login`"
    kind = "subscription (ChatGPT)" if "chatgpt" in out.lower() else "API key" if "api key" in out.lower() else "unknown"
    return True, f"logged in: yes, kind: {kind}"


def check_codex_sandbox() -> tuple[bool, str]:
    remedy = 'add `[windows]` with `sandbox = "unelevated"` to ~/.codex/config.toml (the human edits this file)'
    path = Path.home() / ".codex" / "config.toml"
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return False, remedy
    if data.get("windows", {}).get("sandbox") != "unelevated":
        return False, remedy
    return True, "windows.sandbox = unelevated"


def check_codex_plugin() -> tuple[bool, str]:
    code, out = run(["claude", "plugin", "list"])
    if code != 0 or "codex@openai-codex" not in out:
        return False, "inside Claude Code install the plugin codex@openai-codex (only needed for /codex:review)"
    return True, "codex@openai-codex present"


def check_node() -> tuple[bool, str]:
    code, out = run(["node", "--version"])
    if code != 0:
        return False, "install Node.js"
    return True, f"version {'.'.join(map(str, version_of(out) or ()))}"


def check_git() -> tuple[bool, str]:
    code, out = run(["git", "--version"])
    if code != 0:
        return False, "install Git for Windows"
    return True, f"version {'.'.join(map(str, version_of(out) or ()))}"


def check_python() -> tuple[bool, str]:
    shown = ".".join(map(str, sys.version_info[:3]))
    if sys.version_info[:2] < PYTHON_MIN:
        return False, f"version {shown}; install Python 3.11 or newer"
    return True, f"version {shown}"


def check_uv() -> tuple[bool, str]:
    code, out = run(["uv", "--version"])
    if code != 0:
        return False, "install uv"
    return True, f"version {'.'.join(map(str, version_of(out) or ()))}"


def check_powershell() -> tuple[bool, str]:
    code, out = run(["powershell.exe", "-NoProfile", "-Command", "$PSVersionTable.PSVersion.ToString()"])
    if code != 0:
        return False, "Windows PowerShell (powershell.exe) not found; this tool is evidenced on Windows only"
    return True, f"version {out.strip()}"


def check_gh() -> tuple[bool, str]:
    code, _ = run(["gh", "--version"])
    if code != 0:
        return False, "install the GitHub CLI (only needed for review mode on a GitHub PR)"
    code, _ = run(["gh", "auth", "status"])
    if code != 0:
        return False, "logged in: no; run `gh auth login` (only needed for review mode on a GitHub PR)"
    return True, "logged in: yes"


CHECKS = {
    "claude-cli": check_claude_cli,
    "claude-login": check_claude_login,
    "codex-cli": check_codex_cli,
    "codex-login": check_codex_login,
    "codex-sandbox": check_codex_sandbox,
    "codex-plugin": check_codex_plugin,
    "node": check_node,
    "git": check_git,
    "python": check_python,
    "uv": check_uv,
    "powershell": check_powershell,
    "gh": check_gh,
}


def table_rows() -> list[tuple[str, bool]]:
    """Return (id, required) for every data row of the table whose first header cell is `id`."""
    rows = []
    in_table = False
    for line in PREREQUISITES.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")] if line.startswith("|") else []
        if not cells:
            in_table = False
            continue
        if cells[0] == "id":
            in_table = True
            continue
        if in_table and not set(cells[0]) <= set("-: "):
            rows.append((cells[0], cells[4] == "required"))
    return rows


def main() -> int:
    rows = table_rows()
    ids = [i for i, _ in rows]
    unmatched = sorted(set(ids) ^ set(CHECKS))
    if unmatched or len(ids) != len(set(ids)):
        sys.stdout.write(f"doctor: PREREQUISITES.md and doctor.py disagree on: {', '.join(unmatched) or 'duplicate ids'}\n")
        return 1
    failed = 0
    for row_id, required in rows:
        ok, detail = CHECKS[row_id]()
        status = "ok" if ok else "missing" if required else "optional-missing"
        sys.stdout.write(f"{status} {row_id}: {detail}\n")
        failed += 0 if ok or not required else 1
    sys.stdout.write("doctor: OK\n" if failed == 0 else f"doctor: FAIL {failed}\n")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
