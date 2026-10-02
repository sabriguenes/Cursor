#
# second-opinion eval fixture: harness_probe.
#
# Synthetic playground module. Covered by the license of the repository
# that contains it.
#

"""Reply-to addresses taken from paper front matter lines."""

def reply_addresses(lines: list[str]) -> list[str]:
    found: list[str] = []
    for line in lines:
        text = line.strip()
        if not text:
            continue
        start = text.rfind("<")
        end = text.rfind(">")
        if start < 0 or end < start:
            found.append(text)
            continue
        found.append(text[start + 1 : end])
    if not found:
        return found
    return found[:-1]
