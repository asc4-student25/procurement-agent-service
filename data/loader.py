"""Mock data loader — single point of access for all reference data files.

All functions resolve paths relative to the project root (the directory
containing mock_data/). No other module should import from mock_data/ directly.
"""

from __future__ import annotations

import json
from pathlib import Path

# Project root is one level up from this file (data/loader.py -> root)
_ROOT = Path(__file__).resolve().parent.parent / "mock_data"


def _load(filename: str) -> list[dict[str, object]]:
    """Read and parse a JSON file from mock_data/."""
    path = _ROOT / filename
    if not path.exists():
        raise FileNotFoundError(f"Mock data file not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"Mock data file must contain a list of records: {path}")
    return data


def load_budgets() -> list[dict[str, object]]:
    """Return all cost center budget records from mock_data/budgets.json."""
    return _load("budgets.json")


def load_vendors() -> list[dict[str, object]]:
    """Return all vendor records from mock_data/vendors.json."""
    return _load("vendors.json")


def load_policies() -> list[dict[str, object]]:
    """Return all procurement policy records from mock_data/policies.json."""
    return _load("policies.json")


def load_requests() -> list[dict[str, object]]:
    """Return all sample purchase request records from mock_data/requests.json."""
    return _load("requests.json")
