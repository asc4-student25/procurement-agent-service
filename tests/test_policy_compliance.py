"""Unit tests for the policy compliance tool."""

from __future__ import annotations

from tools.policy_compliance import check_policy_compliance


def test_catering_always_denied() -> None:
    """POL-004 / REQ-009: catering request at $3,200 is denied."""
    result = check_policy_compliance("V-017", "catering", 3_200.00)
    assert result["violation_count"] >= 1
    policy_ids = [violation["policy_id"] for violation in result["violations"]]
    assert "POL-004" in policy_ids
    forced = [
        violation["forced_decision"]
        for violation in result["violations"]
        if violation["policy_id"] == "POL-004"
    ]
    assert forced[0] == "deny"


def test_compliance_flagged_vendor_escalates() -> None:
    """POL-006: V-006 has a compliance flag and must escalate."""
    result = check_policy_compliance("V-006", "professional_services", 35_000.00)
    assert result["highest_severity"] == "escalate"
    policy_ids = [violation["policy_id"] for violation in result["violations"]]
    assert "POL-006" in policy_ids


def test_expired_contract_vendor_denied() -> None:
    """POL-005 / REQ-007: Crestview Print (V-010) expired contract must deny."""
    result = check_policy_compliance("V-010", "marketing_materials", 5_400.00)
    policy_ids = [violation["policy_id"] for violation in result["violations"]]
    assert "POL-005" in policy_ids
    forced = [
        violation["forced_decision"]
        for violation in result["violations"]
        if violation["policy_id"] == "POL-005"
    ]
    assert forced[0] == "deny"


def test_director_threshold_escalates() -> None:
    """POL-003: amount >= $50,000 requires director approval and escalation."""
    result = check_policy_compliance("V-002", "software_licenses", 50_000.00)
    assert result["highest_severity"] == "escalate"
    policy_ids = [violation["policy_id"] for violation in result["violations"]]
    assert "POL-003" in policy_ids


def test_near_threshold_escalates() -> None:
    """POL-003 near-threshold: $47,500 is within 5% of $50,000 and escalates."""
    result = check_policy_compliance("V-016", "hardware", 47_500.00)
    assert result["highest_severity"] == "escalate"
    policy_ids = [violation["policy_id"] for violation in result["violations"]]
    assert "POL-003" in policy_ids


def test_pol001_signal_is_reported_for_threshold_conflict() -> None:
    """POL-001 should be emitted above threshold with active same-category conflicts."""
    result = check_policy_compliance("V-012", "office_supplies", 28_500.00)
    policy_ids = [violation["policy_id"] for violation in result["violations"]]
    assert "POL-001" in policy_ids


def test_pol002_signal_when_manager_approval_missing() -> None:
    """POL-002 should be emitted when manager approval is explicitly missing."""
    result = check_policy_compliance(
        "V-002",
        "software_licenses",
        24_000.00,
        manager_approval_present=False,
    )
    policy_ids = [violation["policy_id"] for violation in result["violations"]]
    assert "POL-002" in policy_ids
    assert result["highest_severity"] == "escalate"


def test_pol002_lower_boundary_requires_manager_approval() -> None:
    """POL-002 lower boundary: $10,000 with missing manager approval should escalate."""
    result = check_policy_compliance(
        "V-002",
        "software_licenses",
        10_000.00,
        manager_approval_present=False,
    )
    policy_ids = [violation["policy_id"] for violation in result["violations"]]
    assert "POL-002" in policy_ids
    assert result["highest_severity"] == "escalate"


def test_pol002_upper_boundary_requires_manager_approval() -> None:
    """POL-002 upper boundary: $49,999 with missing manager approval should escalate."""
    result = check_policy_compliance(
        "V-002",
        "software_licenses",
        49_999.00,
        manager_approval_present=False,
    )
    policy_ids = [violation["policy_id"] for violation in result["violations"]]
    assert "POL-002" in policy_ids
    assert result["highest_severity"] == "escalate"


def test_pol008_signal_when_budget_is_exceeded() -> None:
    """POL-008 should be emitted when request exceeds remaining cost center budget."""
    result = check_policy_compliance(
        "V-007",
        "facilities",
        11_200.00,
        cost_center_id="CC-003",
    )
    policy_ids = [violation["policy_id"] for violation in result["violations"]]
    assert "POL-008" in policy_ids


def test_clean_request_has_no_violations() -> None:
    """A low-amount clean request with no explicit process gaps returns no violations."""
    result = check_policy_compliance("V-002", "software_licenses", 24_000.00)
    assert result["violation_count"] == 0
    assert result["highest_severity"] == "none"
    assert result["violations"] == []


def test_result_always_contains_required_keys() -> None:
    """Every result must contain violations, violation_count, and highest_severity."""
    result = check_policy_compliance("V-007", "facilities", 8_500.00)
    assert "violations" in result
    assert "violation_count" in result
    assert "highest_severity" in result


def test_highest_severity_escalate_takes_priority_over_deny() -> None:
    """When both deny and escalate violations apply, highest_severity must be escalate."""
    result = check_policy_compliance("V-006", "catering", 5_000.00)
    assert result["highest_severity"] == "escalate"


def test_highest_severity_escalate_wins_with_pol008_and_pol006() -> None:
    """Escalate precedence must hold even when POL-008 deny is also present."""
    result = check_policy_compliance(
        "V-006",
        "professional_services",
        40_000.00,
        cost_center_id="CC-009",
    )
    policy_ids = [violation["policy_id"] for violation in result["violations"]]
    assert "POL-006" in policy_ids
    assert "POL-008" in policy_ids
    assert result["highest_severity"] == "escalate"
