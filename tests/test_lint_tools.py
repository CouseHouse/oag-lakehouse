"""The repo's own lint checks pass on the repo."""

from tools import check_emdash, check_hosted_import


def test_no_em_dashes_in_tracked_markdown() -> None:
    assert check_emdash.main() == 0


def test_hosted_adapter_not_imported_outside_evals() -> None:
    assert check_hosted_import.main() == 0
