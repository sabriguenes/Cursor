# SPDX-License-Identifier: MIT
"""Static check of foreman.md, without any model call.

Usage: python -B skill_check.py [path/to/foreman.md]
Default target: foreman.md one folder above this script.
scripts/ and maintainers/ are resolved next to the target.

Checks:
1. caps:     foreman.md lines, run.ps1 lines, MUST/NEVER/ALWAYS count
2. tags:     every instruction tag is named by the pattern, stands alone and undecorated
             on its line with a blank line before and after (end of file counts as one),
             opens and closes exactly once in that order, and its block stays within the line cap
3. approved: the human-facing text is byte-equal to the approved text
4. version:  the `Version:` line equals the newest `## <version>` in maintainers/CHANGELOG.md
5. banned:   no term of maintainers/banned-terms.txt in the target, scripts/ or maintainers/
6. refs:     every `section "X"` names an existing heading
7. links:    every relative Markdown link and backtick path under scripts/ or maintainers/ exists

Exit 0 when all checks pass, 1 otherwise.
"""

import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_TARGET = SCRIPT_DIR.parent / "foreman.md"

MAX_TOOL_LINES = 470
MAX_RUNNER_LINES = 220
MAX_BLOCK_LINES = 30
MAX_SCHEMA_BLOCK_LINES = 56
MAX_HARD_WORDS = 3
SCHEMA_TAG = "review-schema-instructions"
EXPECTED_TAGS = (
    "review-schema-instructions",
    "planning-instructions",
    "step-instructions",
    "verdict-instructions",
    "opus-review-instructions",
    "plan-review-instructions",
    "step-review-instructions",
    "codex-review-instructions",
    "develop-mode-instructions",
    "review-mode-instructions",
    "sweep-mode-instructions",
    "setup-mode-instructions",
    "prerequisites-instructions",
    "coverage-instructions",
)
APPROVED_TEXT = "\n\n".join(
    (
        "# The Foreman",
        "I build nothing. Ask anyone on the site; they will tell you the same, usually with some relief. "
        "You bring drawings. I read them once, all the way through, and then I hand them out: the bricklayer "
        "gets the walls, the inspector gets the walls after the bricklayer, and the inspector writes his notes "
        "before he reads the bricklayer's. The bricklayer is good. He is fast, he is careful, and he is certain, "
        "which is the part that needs watching. The inspector is good too. He touches nothing, signs nothing, "
        "and writes down everything he would not have built that way. When they disagree I do not take sides. "
        "I put a level on the wall. If the bubble moves, the inspector was right. If it does not, the wall "
        "stays, and his note goes in the file with the reading next to it.",
        "Some questions are not mine and not theirs. Where the door goes, whether the old wall comes down, "
        "anything that cannot be put back by Monday: those go to you, one at a time, with what the crew will "
        "do if you say nothing. Everything else I settle on site and write down. Every evening the site book "
        "is current, so whoever opens the gate tomorrow, me or a stranger, can read where we stopped and lay "
        "the next course. Nobody leaves with the keys. The truck that carries it off the site is yours to drive.",
        "Mention this file in Cursor's agent chat with a mode and its subject: `develop` with a plan or a task, "
        "`review` with a pull request, `sweep` with a module. Opus builds in the Claude Code CLI, Codex inspects "
        "read-only in the Codex CLI, and every run is recorded under `.foreman/runs/` in the target repo. To "
        "continue an interrupted run from a fresh chat, mention the file again and say resume.",
    )
)
NORMATIVE_HEADING = "## Normative Instructions"
TEXT_SUFFIXES = {".md", ".txt", ".ps1", ".py", ".json", ".diff", ".toml", ".yml"}
PATH_PREFIXES = ("scripts/", "maintainers/")
PLACEHOLDER_CHARS = set("<>*{}|$")

TAG_NAME_RE = re.compile(r"^[a-z]+(-[a-z]+){0,2}-instructions$")
TAG_LIKE_RE = re.compile(r"<(/?)([A-Za-z0-9_-]*-instructions)>")
HARD_WORD_RE = re.compile(r"\b(MUST|NEVER|ALWAYS)\b")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*$")
REF_RE = re.compile(r'section "([^"\n]+)"')
BACKTICK_RE = re.compile(r"`([^`\n]+)`")
LINK_RE = re.compile(r"\]\(([^)\s]+)\)")
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


def check_caps(name: str, text: str, base: Path) -> list[str]:
    errors = []
    count = len(text.splitlines())
    if count > MAX_TOOL_LINES:
        errors.append(f"{name}: {count} lines, cap {MAX_TOOL_LINES}")
    runner = base / "scripts" / "run.ps1"
    if not runner.exists():
        errors.append("scripts/run.ps1 missing next to the tool file")
    else:
        count = len(runner.read_text(encoding="utf-8-sig").splitlines())
        if count > MAX_RUNNER_LINES:
            errors.append(f"scripts/run.ps1: {count} lines, cap {MAX_RUNNER_LINES}")
    hard = len(HARD_WORD_RE.findall(text))
    if hard > MAX_HARD_WORDS:
        errors.append(f"{name}: MUST/NEVER/ALWAYS {hard}x, cap {MAX_HARD_WORDS}")
    return errors


def check_tags(name: str, text: str) -> list[str]:
    lines = text.splitlines()
    errors = []
    found: dict[str, tuple[list[int], list[int]]] = {}
    for i, line in enumerate(lines):
        for slash, tag in TAG_LIKE_RE.findall(line):
            opens, closes = found.setdefault(tag, ([], []))
            (closes if slash else opens).append(i)
            if line != f"<{slash}{tag}>":
                errors.append(f"{name}:{i + 1}: tag <{slash}{tag}> decorated or indented")
            elif i == 0 or lines[i - 1] != "" or (i + 1 < len(lines) and lines[i + 1] != ""):
                errors.append(f"{name}:{i + 1}: tag <{slash}{tag}> lacks a blank line before or after")
    for tag in sorted(set(EXPECTED_TAGS) - set(found)):
        errors.append(f"{name}: tag <{tag}> missing")
    for tag, (opens, closes) in sorted(found.items()):
        if not TAG_NAME_RE.match(tag):
            errors.append(f"{name}: tag <{tag}> does not match {TAG_NAME_RE.pattern}")
        elif tag not in EXPECTED_TAGS:
            errors.append(f"{name}: tag <{tag}> is not a known block")
        if len(opens) != 1 or len(closes) != 1 or opens[0] > closes[0]:
            errors.append(f"{name}: tag <{tag}> opens {len(opens)}x, closes {len(closes)}x or out of order")
            continue
        size = closes[0] - opens[0] + 1
        cap = MAX_SCHEMA_BLOCK_LINES if tag == SCHEMA_TAG else MAX_BLOCK_LINES
        if size > cap:
            errors.append(f"{name}:{opens[0] + 1}: block <{tag}> {size} lines, cap {cap}")
    return errors


def check_approved(name: str, raw: str) -> list[str]:
    head, sep, _ = raw.partition(f"\n{NORMATIVE_HEADING}\n")
    _, comment_end, human = head.partition("-->\n")
    if not sep or not comment_end:
        return [f"{name}: no HTML comment followed by `{NORMATIVE_HEADING}`"]
    if human.strip("\n").encode("utf-8") != APPROVED_TEXT.encode("utf-8"):
        return [f"{name}: human-facing text differs from the approved text"]
    return []


def check_version(name: str, text: str, base: Path) -> list[str]:
    version = VERSION_RE.search(text)
    if version is None:
        return [f"{name}: no `Version:` line"]
    changelog = base / "maintainers" / "CHANGELOG.md"
    if not changelog.exists():
        return ["maintainers/CHANGELOG.md missing"]
    newest = CHANGELOG_RE.search(changelog.read_text(encoding="utf-8"))
    if newest is None:
        return ["maintainers/CHANGELOG.md: no heading of the form `## <version>`"]
    if newest.group(1) != version.group(1):
        return [f"version mismatch: {name} {version.group(1)}, CHANGELOG.md {newest.group(1)}"]
    return []


def banned_terms(path: Path) -> list[str]:
    raw = path.read_text(encoding="utf-8").splitlines()
    return sorted({t.strip() for t in raw if t.strip() and not t.lstrip().startswith("#")})


def is_exempt(path: Path, base: Path) -> bool:
    if path == base / "maintainers" / "banned-terms.txt":
        return True
    return path.parent == base / "maintainers" / "evals" and path.name.startswith("baseline-")


def check_banned(target: Path, base: Path) -> list[str]:
    terms_file = base / "maintainers" / "banned-terms.txt"
    if not terms_file.exists():
        return ["maintainers/banned-terms.txt missing"]
    terms = banned_terms(terms_file)
    files = [target] + sorted(
        p
        for folder in (base / "scripts", base / "maintainers")
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


def check_refs(name: str, lines: list[tuple[int, str]]) -> list[str]:
    headings = {m.group(1) for _, line in lines if (m := HEADING_RE.match(line))}
    return [
        f'{name}:{no}: section "{ref}" has no heading'
        for no, line in lines
        for ref in REF_RE.findall(line)
        if ref not in headings
    ]


def check_links(name: str, lines: list[tuple[int, str]], base: Path) -> list[str]:
    errors = []
    for no, line in lines:
        for link in LINK_RE.findall(line):
            target = link.split("#", 1)[0]
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            if not (base / target).exists():
                errors.append(f"{name}:{no}: link `{link}` does not resolve")
        for span in BACKTICK_RE.findall(line):
            candidate = span.strip().rstrip(".,:;")
            if " " in candidate or not candidate.startswith(PATH_PREFIXES):
                continue
            if PLACEHOLDER_CHARS & set(candidate) or "..." in candidate:
                continue
            if not (base / candidate).exists():
                errors.append(f"{name}:{no}: path `{candidate}` does not exist")
    return errors


def main() -> int:
    target = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_TARGET
    base = target.parent
    raw = target.read_bytes().decode("utf-8").replace("\r\n", "\n")
    lines = prose_lines(raw)
    results = {
        "caps": check_caps(target.name, raw, base),
        "tags": check_tags(target.name, raw),
        "approved": check_approved(target.name, raw),
        "version": check_version(target.name, raw, base),
        "banned": check_banned(target, base),
        "refs": check_refs(target.name, lines),
        "links": check_links(target.name, lines, base),
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
