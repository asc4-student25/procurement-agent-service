"""Unit tests for the vendor duplication check tool (POL-001)."""

from __future__ import annotations

import pytest

from tools.vendor_duplication import check_vendor_duplication


def test_no_violation_below_threshold() -> None:
    """Amount at or below $25,000 never triggers POL-001 regardless of category."""
    result = check_vendor_duplication("V-012", "office_supplies", 25_000.00)
    assert result["violation"] is False
    assert "threshold" in result["reason"].lower()


def test_violation_office_supplies_above_threshold() -> None:
    """REQ-008: NovaPrint office_supplies $28,500 with active conflicts -> violation."""
    result = check_vendor_duplication("V-012", "office_supplies", 28_500.00)
    assert result["violation"] is True
    assert len(result["conflicting_vendor_ids"]) > 0
    assert "POL-001" in result["reason"]


def test_req008_conflicts_are_exact_office_supplies_contract_vendors() -> None:
    """REQ-008: NovaPrint should conflict with contracted vendors V-001 and V-003."""
    result = check_vendor_duplication("V-012", "office_supplies", 28_500.00)

    assert result["violation"] is True
    assert set(result["conflicting_vendor_ids"]) == {"V-001", "V-003"}
    assert set(result["conflicting_vendor_names"]) == {
        "Apex Office Supplies",
        "Meridian Office Products",
    }
    assert "POL-001" in result["reason"]


def test_no_violation_sole_active_vendor_in_category() -> None:
    """If no other vendor holds an active contract in the category, no violation."""
    result = check_vendor_duplication("V-017", "catering", 30_000.00)
    assert result["violation"] is False


def test_no_violation_for_category_outside_pol001() -> None:
    """POL-001 does not apply to categories outside affected_categories."""
    result = check_vendor_duplication("V-015", "training", 40_000.00)
    assert result["violation"] is False
    assert "not governed by POL-001" in result["reason"]


def test_result_contains_required_keys() -> None:
    """Every result must contain the standard response keys."""
    result = check_vendor_duplication("V-002", "software_licenses", 5_000.00)
    for key in (
        "violation",
        "vendor_id",
        "category",
        "amount",
        "conflicting_vendor_ids",
        "conflicting_vendor_names",
        "reason",
    ):
        assert key in result, f"Missing key: {key}"


def test_vendor_id_echoed_in_result() -> None:
    """The vendor_id in the result must match the input."""
    result = check_vendor_duplication("V-007", "facilities", 10_000.00)
    assert result["vendor_id"] == "V-007"


def test_amount_echoed_in_result() -> None:
    """The amount in the result must match the input."""
    result = check_vendor_duplication("V-002", "software_licenses", 24_000.00)
    assert result["amount"] == pytest.approx(24_000.00)
