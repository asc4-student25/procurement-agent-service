"""Risk assessment tool for vendor compliance and contract status."""

from __future__ import annotations

from typing import Literal

try:
    from data.loader import load_vendors
except ImportError:  # pragma: no cover - temporary fallback while repo is being aligned
    from solutions.data.loader import load_vendors

RiskLevel = Literal["low", "medium", "high", "critical"]
_KNOWN_CONTRACT_STATUSES = {"active", "expired", "none"}
_ALLOWED_RISK_LEVELS: set[RiskLevel] = {"low", "medium", "high", "critical"}


def _error_payload(vendor_id: str, message: str) -> dict[str, object]:
    """Return a structured fallback response when risk assessment cannot complete."""
    return {
        "error": message,
        "vendor_id": vendor_id,
        "vendor_name": "Unknown",
        "compliance_flag": False,
        "compliance_notes": "",
        "contract_status": "unknown",
        "risk_level": "critical",
        "risk_summary": "Risk data unavailable; escalate for manual review.",
    }


def assess_risk(vendor_id: str) -> dict[str, object]:
    """Assess vendor risk for procurement decision support.

    Classification contract:
    - ``critical``: compliance flag is active
    - ``high``: contract is expired
    - ``medium``: no contract exists
    - ``low``: active contract and no compliance flag

    Returns required keys on all paths, including structured ``error`` context
    when vendor lookup or data loading fails.
    """
    try:
        vendors = load_vendors()
    except Exception as exc:
        return _error_payload(vendor_id, f"Vendor data could not be loaded: {exc}")

    vendor = next((item for item in vendors if item.get("vendor_id") == vendor_id), None)
    if vendor is None:
        payload = _error_payload(vendor_id, f"Vendor '{vendor_id}' not found in vendor data.")
        payload["risk_level"] = "high"
        payload[
            "risk_summary"
        ] = "Vendor is unknown to procurement records; verify vendor identity before proceeding."
        return payload

    compliance_flag = bool(vendor.get("compliance_flag", False))
    compliance_notes = str(vendor.get("compliance_notes", ""))
    contract_status = str(vendor.get("contract_status", "none"))
    if contract_status not in _KNOWN_CONTRACT_STATUSES:
        contract_status = "none"

    if compliance_flag:
        risk_level: RiskLevel = "critical"
        risk_summary = (
            "Vendor has an active compliance flag; Legal and Compliance review is required."
        )
    elif contract_status == "expired":
        risk_level = "high"
        risk_summary = "Vendor contract is expired; do not proceed without contract remediation."
    elif contract_status == "none":
        risk_level = "medium"
        risk_summary = "Vendor has no active contract; additional due diligence is required."
    else:
        risk_level = "low"
        risk_summary = "Vendor has an active contract and no compliance concerns."

    if risk_level not in _ALLOWED_RISK_LEVELS:
        return _error_payload(vendor_id, "Risk classification produced an invalid risk level.")

    return {
        "vendor_id": vendor_id,
        "vendor_name": str(vendor.get("name", "")),
        "compliance_flag": compliance_flag,
        "compliance_notes": compliance_notes,
        "contract_status": contract_status,
        "risk_level": risk_level,
        "risk_summary": risk_summary,
    }