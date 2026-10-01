# SPDX-License-Identifier: MIT
"""Copy one prompt block of second-opinion.md into a prompt file, word for word.

Usage: python -B make_prompt.py <tag> <out-file> [NAME=value | NAME=@file ...]

The block between the lines `<tag>` and `</tag>` is copied unchanged, except that
every placeholder `<NAME>` is replaced by its value. `NAME=@file` reads the value
from a UTF-8 file, for values with several lines.

Exit 1 when the tag is missing, a placeholder has no value, a value is unused,
or a value contains the tool folder's path. The prompt file is then not written.
"""

import hashlib
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
TOOL_DIR = SCRIPT_DIR.parent
TOOL_FILE = TOOL_DIR / "second-opinion.md"
PLACEHOLDER_RE = re.compile(r"<([A-Z][A-Z0-9_]*)>")
HASH_CHARS = 12


def fail(message: str) -> int:
    sys.stdout.write(f"make_prompt: FAIL {message}\n")
    return 1


def block(tag: str) -> str | None:
    lines = TOOL_FILE.read_text(encoding="utf-8").splitlines()
    opens = [i for i, line in enumerate(lines) if line == f"<{tag}>"]
    closes = [i for i, line in enumerate(lines) if line == f"</{tag}>"]
    if len(opens) != 1 or len(closes) != 1 or opens[0] > closes[0]:
        return None
    return "\n".join(lines[opens[0] + 1 : closes[0]]).strip("\n") + "\n"


def parse_values(pairs: list[str]) -> dict[str, str] | str:
    values = {}
    for pair in pairs:
        name, sep, value = pair.partition("=")
        if not sep or not PLACEHOLDER_RE.fullmatch(f"<{name}>"):
            return f"bad argument {pair.split('=')[0]!r}, expected NAME=value"
        if value.startswith("@"):
            source = Path(value[1:])
            if not source.is_file():
                return f"value file for {name} not found"
            value = source.read_text(encoding="utf-8").strip("\n")
        values[name] = value
    return values


def leaks_tool_dir(value: str) -> bool:
    lowered = value.lower().replace("\\", "/")
    return str(TOOL_DIR).lower().replace("\\", "/") in lowered


def main() -> int:
    if len(sys.argv) < 3:
        return fail("usage: make_prompt.py <tag> <out-file> [NAME=value ...]")
    tag, out = sys.argv[1], Path(sys.argv[2])
    if not tag.endswith("-prompt"):
        return fail(f"{tag} is not a prompt block")
    text = block(tag)
    if text is None:
        return fail(f"block <{tag}> not found exactly once")
    values = parse_values(sys.argv[3:])
    if isinstance(values, str):
        return fail(values)
    needed = set(PLACEHOLDER_RE.findall(text))
    missing = sorted(needed - values.keys())
    unused = sorted(values.keys() - needed)
    if missing:
        return fail(f"no value for {', '.join(missing)}")
    if unused:
        return fail(f"unused value {', '.join(unused)}")
    leaking = sorted(name for name, value in values.items() if leaks_tool_dir(value))
    if leaking:
        return fail(f"value of {', '.join(leaking)} contains the tool folder path")
    prompt = PLACEHOLDER_RE.sub(lambda m: values[m.group(1)], text)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(prompt.encode("utf-8"))
    digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:HASH_CHARS]
    sys.stdout.write(f"prompt: {out.name} ({len(prompt)} chars, sha256 {digest})\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
