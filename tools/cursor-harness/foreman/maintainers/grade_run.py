# SPDX-License-Identifier: MIT
"""Grade one run folder from its logs, without any model call.

Usage: python -B grade_run.py <run-dir> <rules.json> [--worktree <path>]

<run-dir> is one run folder under .foreman/runs/ in the target repo.
Reads every logs/stream-*.jsonl of the run (UTF-8 or UTF-16), classifies each as a
Claude stream (system/init) or a Codex stream (thread.started), and checks the rules:

  runner_denies          patterns that ../scripts/run.ps1 must pass to --disallowedTools
  reject_commands        regexes no shell command of Claude or Codex may match
  allow_edit_paths       regexes; every Edit/Write/MultiEdit/NotebookEdit path must match one (checked only when present)
  expect_denied          regexes; each must match at least one permission denial
  json_artifacts         run-relative paths that must exist and validate against the review-schema-instructions block of ../foreman.md
  markdown_artifacts     {path: status line}; file must exist, be non-empty, end with exactly that line once
  reject_output          regexes no final answer or artifact may match (canaries)
  expect_output          regexes at least one final answer or artifact must match
  worktree_clean_except  regexes; with --worktree, `git status --porcelain` may only list matching paths
  expect_read_full       worktree-relative files every reviewer must read in full

Every rule is golden. Prints one line per check, the score, the models and the Codex tokens.
Exit 0 all checks pass, 2 a golden check failed, 3 bad input.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent.parent
RUNNER = TOOL_DIR / "scripts" / "run.ps1"
TOOL_FILE = TOOL_DIR / "foreman.md"
SCHEMA_TAG = "review-schema-instructions"
EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
SHELL_TOOLS = {"Bash", "PowerShell"}
READ_TOOL = "Read"
CODEX_SESSIONS = Path.home() / ".codex" / "sessions"
TOKEN_FIELDS = ("input_tokens", "cached_input_tokens", "cache_write_input_tokens", "output_tokens",
                "reasoning_output_tokens")


def read_text(path: Path) -> str:
    raw = path.read_bytes()
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16")
    return raw.decode("utf-8-sig", errors="replace")


def events(path: Path) -> list[dict]:
    out = []
    for line in read_text(path).splitlines():
        if line.strip():
            try:
                out.append(json.loads(line))
            except ValueError:
                continue
    return out


def review_schema() -> dict:
    lines = TOOL_FILE.read_text(encoding="utf-8").splitlines()
    opening, closing = f"<{SCHEMA_TAG}>", f"</{SCHEMA_TAG}>"
    if lines.count(opening) != 1 or lines.count(closing) != 1 or lines.index(opening) > lines.index(closing):
        raise ValueError(f"{TOOL_FILE.name}: {SCHEMA_TAG} must occur once, opening then closing")
    return json.loads("\n".join(lines[lines.index(opening) + 1:lines.index(closing)]))


def validate(value, schema: dict, where: str = "$") -> list[str]:
    """Minimal JSON Schema subset used by review.schema.json."""
    errors = []
    kinds = schema.get("type")
    kinds = [kinds] if isinstance(kinds, str) else kinds or []
    type_ok = {
        "object": isinstance(value, dict), "array": isinstance(value, list),
        "string": isinstance(value, str), "null": value is None,
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
    }
    if kinds and not any(type_ok.get(k, False) for k in kinds):
        return [f"{where}: type {type(value).__name__} not in {kinds}"]
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{where}: {value!r} not in enum")
    if isinstance(value, str) and len(value) < schema.get("minLength", 0):
        errors.append(f"{where}: shorter than minLength")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{where}: below minimum")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{where}: above maximum")
    if isinstance(value, dict):
        props = schema.get("properties", {})
        errors += [f"{where}: missing {k}" for k in schema.get("required", []) if k not in value]
        if schema.get("additionalProperties") is False:
            errors += [f"{where}: extra {k}" for k in value if k not in props]
        for k, v in value.items():
            if k in props:
                errors += validate(v, props[k], f"{where}.{k}")
    if isinstance(value, list) and "items" in schema:
        for i, item in enumerate(value):
            errors += validate(item, schema["items"], f"{where}[{i}]")
    return errors


class Stream:
    def __init__(self, path: Path):
        self.path = path
        self.events = events(path)
        self.kind = "other"
        self.model = None
        self.thread = None
        self.tool_calls: list[tuple[str, dict]] = []
        self.tool_outputs: list[str] = []
        self.denials: list[dict] = []
        self.answers: list[str] = []
        self.tokens = dict.fromkeys(TOKEN_FIELDS, 0)
        self.codex_commands: list[tuple[str, str]] = []
        for ev in self.events:
            self._take(ev)

    def _take(self, ev: dict) -> None:
        kind = ev.get("type")
        if kind == "system" and ev.get("subtype") == "init":
            self.kind, self.model = "claude", ev.get("model")
        elif kind == "thread.started":
            self.kind, self.thread = "codex", ev.get("thread_id")
        elif kind in ("assistant", "user"):
            for part in (ev.get("message") or {}).get("content") or []:
                if not isinstance(part, dict):
                    continue
                if part.get("type") == "tool_use":
                    self.tool_calls.append((part.get("name", ""), part.get("input") or {}))
                elif part.get("type") == "tool_result":
                    self.tool_outputs.append(json.dumps(part.get("content"), ensure_ascii=False))
        elif kind == "result":
            self.denials += ev.get("permission_denials") or []
            if isinstance(ev.get("result"), str):
                self.answers.append(ev["result"])
        elif kind == "item.completed":
            item = ev.get("item") or {}
            if item.get("type") == "command_execution":
                self.codex_commands.append((item.get("command") or "", item.get("aggregated_output") or ""))
            elif item.get("type") == "agent_message":
                self.answers.append(item.get("text") or "")
        elif kind == "turn.completed":
            usage = ev.get("usage") or {}
            for field in TOKEN_FIELDS:
                self.tokens[field] += int(usage.get(field) or 0)

    def commands(self) -> list[str]:
        shell = [inp.get("command", "") for name, inp in self.tool_calls if name in SHELL_TOOLS]
        return shell + [cmd for cmd, _ in self.codex_commands]


def codex_model(thread: str | None) -> str | None:
    if not thread or not CODEX_SESSIONS.exists():
        return None
    for rollout in CODEX_SESSIONS.rglob(f"rollout-*{thread}.jsonl"):
        for line in read_text(rollout).splitlines():
            try:
                payload = json.loads(line).get("payload")
            except ValueError:
                continue
            if isinstance(payload, dict) and payload.get("model"):
                return payload["model"]
    return None


def norm(path: str) -> str:
    return path.replace("\\", "/")


def full_read(stream: Stream, rel: str, last_line: str) -> bool:
    """A whole-file Read, or any tool output that reaches the file's last non-empty line."""
    whole = any(name == READ_TOOL and norm(inp.get("file_path", "")).endswith(rel)
                and "limit" not in inp and "offset" not in inp for name, inp in stream.tool_calls)
    escaped = json.dumps(last_line, ensure_ascii=False)[1:-1]
    outputs = stream.tool_outputs + [out for _, out in stream.codex_commands]
    return whole or any(last_line in out or escaped in out for out in outputs)


def grade(run_dir: Path, rules: dict, worktree: Path | None) -> list[tuple[str, bool, str]]:
    streams = [Stream(p) for p in sorted((run_dir / "logs").glob("stream-*.jsonl"))]
    checks: list[tuple[str, bool, str]] = []

    runner = RUNNER.read_text(encoding="utf-8")
    for pattern in rules.get("runner_denies", []):
        checks.append((f"runner denies {pattern}", pattern in runner, ""))

    for pattern in rules.get("reject_commands", []):
        hits = [f"{s.path.name}: {c[:80]}" for s in streams for c in s.commands() if re.search(pattern, c)]
        checks.append((f"no command matches {pattern}", not hits, "; ".join(hits)))

    if "allow_edit_paths" in rules:
        allowed = rules["allow_edit_paths"]
        edits = [(s.path.name, norm(inp.get("file_path", ""))) for s in streams
                 for name, inp in s.tool_calls if name in EDIT_TOOLS]
        bad = [f"{n}: {p}" for n, p in edits if not any(re.search(a, p) for a in allowed)]
        checks.append(("edits only at allowed paths", not bad, "; ".join(bad)))

    denials = [json.dumps(d, sort_keys=True) for s in streams for d in s.denials]
    for pattern in rules.get("expect_denied", []):
        checks.append((f"denied: {pattern}", any(re.search(pattern, d) for d in denials), ""))

    schema = review_schema() if rules.get("json_artifacts") else {}
    for rel in rules.get("json_artifacts", []):
        path = run_dir / rel
        try:
            errs = validate(json.loads(read_text(path)), schema)
        except (OSError, ValueError) as exc:
            errs = [type(exc).__name__]
        checks.append((f"artifact {rel} valid", not errs, "; ".join(errs[:3])))

    texts = [a for s in streams for a in s.answers]
    for rel, status in rules.get("markdown_artifacts", {}).items():
        path = run_dir / rel
        text = read_text(path) if path.exists() else ""
        lines = [line.rstrip() for line in text.splitlines() if line.strip()]
        ok = bool(lines) and lines[-1] == status and lines.count(status) == 1
        checks.append((f"artifact {rel} ends with {status}", ok, ""))
        texts.append(text)
    texts += [read_text(p) for p in sorted((run_dir / "reviews").glob("*.json"))] if (run_dir / "reviews").exists() else []

    for pattern in rules.get("reject_output", []):
        checks.append((f"no output matches {pattern}", not any(re.search(pattern, t) for t in texts), ""))
    for pattern in rules.get("expect_output", []):
        checks.append((f"output matches {pattern}", any(re.search(pattern, t) for t in texts), ""))

    if worktree is not None:
        status = subprocess.run(["git", "-C", str(worktree), "status", "--porcelain"],
                                capture_output=True, text=True, encoding="utf-8").stdout.splitlines()
        keep = rules.get("worktree_clean_except", [])
        dirty = [line for line in status if not any(re.search(k, line[3:]) for k in keep)]
        checks.append(("worktree clean except allowed paths", not dirty, "; ".join(dirty)))
        reviewers = [s for s in streams if s.kind in ("claude", "codex")]
        for rel in rules.get("expect_read_full", []):
            body = [line for line in (worktree / rel).read_text(encoding="utf-8").splitlines() if line.strip()]
            last = body[-1].strip() if body else ""
            missing = [s.path.name for s in reviewers if not full_read(s, rel, last)]
            checks.append((f"read in full: {rel}", not missing, "; ".join(missing)))
    elif rules.get("worktree_clean_except") is not None or rules.get("expect_read_full"):
        checks.append(("--worktree given for worktree rules", False, "missing --worktree"))

    for s in streams:
        if s.kind == "codex":
            s.model = codex_model(s.thread)
        tokens = " ".join(f"{k}={v}" for k, v in s.tokens.items()) if s.kind == "codex" else ""
        sys.stdout.write(f"stream {s.path.name}: {s.kind} model={s.model} denials={len(s.denials)} {tokens}\n".rstrip() + "\n")
    return checks


def main() -> int:
    args = sys.argv[1:]
    if args in (["--help"], ["-h"]):
        sys.stdout.write(__doc__)
        return 0
    worktree = None
    if "--worktree" in args:
        i = args.index("--worktree")
        worktree = Path(args[i + 1])
        del args[i:i + 2]
    if len(args) != 2:
        sys.stdout.write(__doc__.splitlines()[2] + "\n")
        return 3
    run_dir, rules_path = Path(args[0]), Path(args[1])
    if not (run_dir / "logs").is_dir():
        sys.stdout.write(f"no logs/ in {run_dir}\n")
        return 3
    rules = json.loads(read_text(rules_path))
    checks = grade(run_dir, rules, worktree)
    passed = sum(ok for _, ok, _ in checks)
    for name, ok, detail in checks:
        sys.stdout.write(f"{'pass' if ok else 'FAIL'} {name}{f'  ({detail})' if detail and not ok else ''}\n")
    sys.stdout.write(f"score {passed}/{len(checks)}\n")
    sys.stdout.write("grade_run: OK\n" if passed == len(checks) else "grade_run: FAIL golden\n")
    return 0 if passed == len(checks) else 2


if __name__ == "__main__":
    sys.exit(main())
