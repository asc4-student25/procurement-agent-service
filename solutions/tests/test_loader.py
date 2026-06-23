"""Unit tests for the centralized mock data loader."""

from __future__ import annotations

from pathlib import Path

import pytest

from data import loader


def test_loader_functions_return_lists() -> None:
    """All public loader functions should return list-shaped datasets."""
    assert isinstance(loader.load_budgets(), list)
    assert isinstance(loader.load_vendors(), list)
    assert isinstance(loader.load_policies(), list)
    assert isinstance(loader.load_requests(), list)


def test_loader_works_from_non_root_working_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Loader should resolve fixture files regardless of current process directory."""
    # Move to a random temporary directory to prove resolution is path-independent.
    monkeypatch.chdir(tmp_path)
    budgets = loader.load_budgets()
    assert any(record.get("cost_center_id") == "CC-003" for record in budgets)


def test_missing_file_raises_file_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    """Missing fixtures should surface explicit FileNotFoundError."""
    monkeypatch.setattr(loader, "_ROOT", loader._ROOT / "does-not-exist")
    with pytest.raises(FileNotFoundError):
        loader.load_budgets()
