"""Tests for US-004 risk classification and response contract."""

from __future__ import annotations

from tools.risk_assessment import assess_risk


def test_compliance_flag_yields_critical_risk() -> None:
    result = assess_risk("V-006")
    assert result["risk_level"] == "critical"
    assert result["compliance_flag"] is True


def test_expired_contract_yields_high_risk() -> None:
    result = assess_risk("V-010")
    assert result["risk_level"] == "high"
    assert result["contract_status"] == "expired"


def test_no_contract_yields_medium_risk() -> None:
    result = assess_risk("V-004")
    assert result["risk_level"] == "medium"
    assert result["contract_status"] == "none"


def test_active_clean_contract_yields_low_risk() -> None:
    result = assess_risk("V-002")
    assert result["risk_level"] == "low"
    assert result["compliance_flag"] is False


def test_unknown_vendor_returns_structured_error() -> None:
    result = assess_risk("V-999")
    assert "error" in result
    assert result["vendor_id"] == "V-999"
    assert result["risk_level"] in {"high", "critical"}


def test_risk_response_contract_fields_present() -> None:
    result = assess_risk("V-007")
    expected_fields = {
        "vendor_id",
        "vendor_name",
        "compliance_flag",
        "compliance_notes",
        "contract_status",
        "risk_level",
        "risk_summary",
    }
    assert expected_fields.issubset(result.keys())


def test_risk_level_is_constrained() -> None:
    allowed = {"low", "medium", "high", "critical"}
    for vendor_id in ("V-002", "V-004", "V-006", "V-010", "V-999"):
        result = assess_risk(vendor_id)
        assert result["risk_level"] in allowed


def test_risk_summary_is_non_empty() -> None:
    result = assess_risk("V-013")
    summary = str(result["risk_summary"])  # defensive cast for contract checks
    assert summary.strip()