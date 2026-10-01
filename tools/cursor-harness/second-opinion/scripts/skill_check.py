# SPDX-License-Identifier: MIT
"""Static check of second-opinion.md, without any model call.

Usage: python -B skill_check.py [path/to/second-opinion.md]
Default target: second-opinion.md one folder above this script.
Paths, CHANGELOG.md, scripts/ and evals/ are resolved next to the target.

Checks:
1. refs:    every `section "X"` names an existing heading
2. paths:   every backtick span starting with scripts/ or evals/ exists
3. banned:  no term of scripts/banned-terms.txt in the target, scripts/ or evals/
4. version: the `Version:` line equals the newest `## <version>` in CHANGELOG.md
5. tags:    every block tag opens and closes exactly once, alone on its line

Exit 0 when all checks pass, 1 otherwise.
"""

import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_TARGET = SCRIPT_DIR.parent / "second-opinion.md"

BLOCK_TAGS = (
    "non-normative-human-facing-text",
    "develop-mode",
    "review-mode",
    "sweep-mode",
    "opus-plan-prompt",
    "opus-step-prompt",
    "opus-verdict-prompt",
    "opus-review-prompt",
    "codex-plan-review-prompt",
    "codex-step-review-prompt",
    "codex-pr-review-prompt",
)
TEXT_SUFFIXES = {".md", ".txt", ".ps1", ".py", ".json", ".diff", ".toml", ".yml"}
PATH_PREFIXES = ("scripts/", "evals/")
PLACEHOLDER_CHARS = set("<>*{}|$")

HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*$")
REF_RE = re.compile(r'section "([^"\n]+)"')
BACKTICK_RE = re.compile(r"`([^`\n]+)`")
VERSION_RE = re.compile(r"^Version:\s*(\S+)\s*$", re.MULTILINE)
CHANGELOG_RE = re.compile(r"^## (\d+\.\d+\.\d+)\b", re.MULTILINE)


def prose_lines(text: str) -> list[tuple[int, str]]:
    """Return (line number, line) for every line outside fenced code blocks."""
    out = []
    in_fence = False
    for no, line in enumerate(text.splitlines(), start=1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append((no, line))
    return out


def check_refs(name: str, lines: list[tuple[int, str]]) -> list[str]:
    headings = {m.group(1) for _, line in lines if (m := HEADING_RE.match(line))}
    return [
        f'{name}:{no}: section "{ref}" has no heading'
        for no, line in lines
        for ref in REF_RE.findall(line)
        if ref not in headings
    ]


def check_paths(name: str, lines: list[tuple[int, str]], base: Path) -> list[str]:
    errors = []
    for no, line in lines:
        for span in BACKTICK_RE.findall(line):
            candidate = span.strip().rstrip(".,:;")
            if " " in candidate or not candidate.startswith(PATH_PREFIXES):
                continue
            if PLACEHOLDER_CHARS & set(candidate) or "..." in candidate:
                continue
            if not (base / candidate).exists():
                errors.append(f"{name}:{no}: path `{candidate}` does not exist")
    return errors


def banned_terms(base: Path) -> list[str]:
    raw = (base / "scripts" / "banned-terms.txt").read_text(encoding="utf-8").splitlines()
    return sorted({t.strip() for t in raw if t.strip() and not t.lstrip().startswith("#")})


def is_exempt(path: Path, base: Path) -> bool:
    if path == base / "scripts" / "banned-terms.txt":
        return True
    return path.parent == base / "evals" and path.name.startswith("baseline-")


def check_banned(target: Path, base: Path) -> list[str]:
    terms = banned_terms(base)
    files = [target] + sorted(
        p
        for folder in (base / "scripts", base / "evals")
        for p in folder.rglob("*")
        if p.is_file() and p.suffix in TEXT_SUFFIXES and not is_exempt(p, base)
    )
    errors = []
    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        shown = path.relative_to(base).as_posix()
        for no, line in enumerate(text.splitlines(), start=1):
            errors.extend(f"{shown}:{no}: banned term `{term}`" for term in terms if term in line)
    return errors


def check_version(name: str, text: str, base: Path) -> list[str]:
    version = VERSION_RE.search(text)
    if version is None:
        return [f"{name}: no `Version:` line"]
    changelog = base / "CHANGELOG.md"
    if not changelog.exists():
        return ["CHANGELOG.md missing next to the tool file"]
    newest = CHANGELOG_RE.search(changelog.read_text(encoding="utf-8"))
    if newest is None:
        return ["CHANGELOG.md: no heading of the form `## <version>`"]
    if newest.group(1) != version.group(1):
        return [f"version mismatch: {name} {version.group(1)}, CHANGELOG.md {newest.group(1)}"]
    return []


def check_tags(name: str, text: str) -> list[str]:
    lines = text.splitlines()
    errors = []
    for tag in BLOCK_TAGS:
        opens = [i for i, line in enumerate(lines) if line == f"<{tag}>"]
        closes = [i for i, line in enumerate(lines) if line == f"</{tag}>"]
        if len(opens) != 1 or len(closes) != 1 or opens[0] > closes[0]:
            errors.append(f"{name}: tag <{tag}> opens {len(opens)}x, closes {len(closes)}x or out of order")
    return errors


def main() -> int:
    target = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_TARGET
    base = target.parent
    text = target.read_text(encoding="utf-8")
    lines = prose_lines(text)
    results = {
        "refs": check_refs(target.name, lines),
        "paths": check_paths(target.name, lines, base),
        "banned": check_banned(target, base),
        "version": check_version(target.name, text, base),
        "tags": check_tags(target.name, text),
    }
    failed = 0
    for name, errors in results.items():
        sys.stdout.write(f"{name}: {'OK' if not errors else f'FAIL {len(errors)}'}\n")
        for err in errors:
            sys.stdout.write(f"  {err}\n")
        failed += len(errors)
    sys.stdout.write("skill_check: OK\n" if failed == 0 else f"skill_check: FAIL {failed}\n")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
