from src.parser import parse_revision


def test_parse_revision_trims_and_normalizes() -> None:
    assert parse_revision("  AbC123  ") == "abc123"


def test_parse_revision_rejects_empty_value() -> None:
    try:
        parse_revision("  ")
    except ValueError:
        return
    raise AssertionError("empty revision was accepted")
