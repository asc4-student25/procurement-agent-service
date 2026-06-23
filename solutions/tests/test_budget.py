"""Unit tests for the budget check tool."""

from __future__ import annotations

import pytest

from tools.budget import check_budget


def test_within_budget_returns_true() -> None:
    """A request well within the cost center budget should be approved."""
    # CC-001 has $187,550 remaining; request $24,000
    result = check_budget("CC-001", 24_000.00)
    assert result["within_budget"] is True
    assert result["overage"] == 0.0
    assert result["remaining_budget"] > 24_000.00


def test_over_budget_returns_false() -> None:
    """REQ-006: CC-003 has $6,900 remaining; request $11,200 should be over budget."""
    result = check_budget("CC-003", 11_200.00)
    assert result["within_budget"] is False
    assert result["overage"] == pytest.approx(4_300.00, abs=0.01)
    assert result["remaining_budget"] == pytest.approx(6_900.00, abs=0.01)


def test_exact_budget_boundary_is_within() -> None:
    """A request exactly equal to the remaining budget is within budget."""
    result = check_budget("CC-003", 6_900.00)
    assert result["within_budget"] is True
    assert result["overage"] == 0.0


def test_unknown_cost_center_returns_error() -> None:
    """An unknown cost center should return an error key and within_budget=False."""
    result = check_budget("CC-999", 1_000.00)
    assert result["within_budget"] is False
    assert "error" in result
    assert "CC-999" in result["error"]
    assert result["remaining_budget"] == 0.0
    assert result["overage"] == pytest.approx(1_000.00, abs=0.01)


def test_result_contains_required_keys() -> None:
    """The result dict must always contain the five standard keys."""
    result = check_budget("CC-001", 500.00)
    assert "within_budget" in result
    assert "cost_center_id" in result
    assert "remaining_budget" in result
    assert "requested_amount" in result
    assert "overage" in result


def test_budget_data_unavailable_returns_structured_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """If budget data cannot be loaded, check_budget returns escalation-safe fallback values."""

    def _raise() -> list[dict[str, object]]:
        raise FileNotFoundError("budgets.json missing")

    monkeypatch.setattr("tools.budget.load_budgets", _raise)

    result = check_budget("CC-001", 2_345.67)
    assert result["within_budget"] is False
    assert result["remaining_budget"] == 0.0
    assert result["overage"] == pytest.approx(2_345.67, abs=0.01)
    assert "error" in result


def test_overage_is_rounded_to_two_decimals() -> None:
    """Over-budget calculations should preserve currency-safe two-decimal precision."""
    result = check_budget("CC-003", 6_900.019)
    assert result["within_budget"] is False
    assert result["overage"] == pytest.approx(0.02, abs=0.001)


def test_invalid_remaining_balance_returns_structured_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Malformed budget records should not raise and must return error fallback values."""

    def _bad_data() -> list[dict[str, object]]:
        return [{"cost_center_id": "CC-001", "remaining": "not-a-number"}]

    monkeypatch.setattr("tools.budget.load_budgets", _bad_data)

    result = check_budget("CC-001", 120.50)
    assert result["within_budget"] is False
    assert result["remaining_budget"] == 0.0
    assert result["overage"] == pytest.approx(120.50, abs=0.01)
    assert "error" in result
