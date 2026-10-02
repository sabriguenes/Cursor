#
# Foreman eval fixture: harness_probe.
#
# Synthetic playground module. Covered by the license of the repository
# that contains it.
#

"""Normalization of WG21 paper ids for the harness probe."""

import re

_PAPER_ID_PATTERN = re.compile(r"^[Pp]([0-9]+)(?:[Rr]([0-9]+))?$")


def normalize_paper_id(raw: str) -> str:
    """Return the canonical upper-case form of a ``P`` paper id.

    Raises ``TypeError`` for non-string input and ``ValueError`` for any
    string that is not ``P<digits>`` with an optional ``R<digits>``.
    """
    if not isinstance(raw, str):
        raise TypeError(f"paper id must be str, got {type(raw).__name__}")
    match = _PAPER_ID_PATTERN.fullmatch(raw)
    if match is None:
        raise ValueError(f"invalid WG21 paper id: {raw!r}")
    num, rev = match.groups()
    return f"P{num}" if rev is None else f"P{num}R{rev}"
