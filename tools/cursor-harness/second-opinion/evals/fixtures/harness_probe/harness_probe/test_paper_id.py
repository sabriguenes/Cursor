#
# second-opinion eval fixture: harness_probe.
#
# Synthetic playground module. Covered by the license of the repository
# that contains it.
#

import pytest
from paper_id import normalize_paper_id


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("p7391r3", "P7391R3"),
        ("P7391R3", "P7391R3"),
        ("p7391", "P7391"),
        ("P7391r3", "P7391R3"),
        ("p7391R3", "P7391R3"),
    ],
)
def test_valid_ids_normalize(raw: str, expected: str) -> None:
    assert normalize_paper_id(raw) == expected


@pytest.mark.parametrize("raw", ["p7391r3", "P7391", "p7391R3"])
def test_normalize_is_idempotent(raw: str) -> None:
    once = normalize_paper_id(raw)
    assert normalize_paper_id(once) == once


@pytest.mark.parametrize(
    "raw",
    [
        "",
        " p7391",
        "p7391 ",
        "p",
        "pr3",
        "p7391r",
        "n8812",
        "d7391r3",
        "p7391r3x",
        "7391",
        "p\u0667\u0663\u0669\u0661",
    ],
)
def test_invalid_ids_raise(raw: str) -> None:
    with pytest.raises(ValueError, match="invalid WG21 paper id"):
        normalize_paper_id(raw)


def test_non_string_raises_type_error() -> None:
    with pytest.raises(TypeError):
        normalize_paper_id(7391)  # type: ignore[arg-type]
