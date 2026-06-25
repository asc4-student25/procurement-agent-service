"""Tests for US-005 orchestration, precedence, and output contract."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agent import evaluate_request
from models import ProcurementRecommendation, PurchaseRequest


def _sample_request() -> PurchaseRequest:
    return PurchaseRequest(
        request_id="REQ-TST-001",
        requestor="A. Tester",
        cost_center_id="CC-001",
        vendor_name="BlueSky Cloud Solutions",
        vendor_id="V-002",
        category="software_licenses",
        item_description="Test purchase",
        quantity=5,
        unit_price=1000.0,
        total_amount=5000.0,
    )


def test_all_checks_run_for_every_request(monkeypatch: pytest.MonkeyPatch) -> None:
    request = _sample_request()
    calls: list[str] = []

    def fake_budget(cost_center_id: str, amount: float) -> dict[str, object]:
        calls.append("budget")
        return {
            "within_budget": True,
            "remaining_budget": 100000.0,
            "requested_amount": amount,
            "overage": 0.0,
            "cost_center_id": cost_center_id,
        }

    def fake_duplication(vendor_id: str, category: str, amount: float) -> dict[str, object]:
        calls.append("duplication")
        return {
            "violation": False,
            "vendor_id": vendor_id,
            "category": category,
            "amount": amount,
            "reason": "No conflict",
        }

    def fake_policy(
        vendor_id: str,
        category: str,
        amount: float,
        quantity: int,
    ) -> dict[str, object]:
        calls.append("policy")
        return {"violations": [], "violation_count": 0, "highest_severity": "none"}

    def fake_risk(vendor_id: str) -> dict[str, object]:
        calls.append("risk")
        return {
            "vendor_id": vendor_id,
            "vendor_name": "Stub Vendor",
            "compliance_flag": False,
            "compliance_notes": "",
            "contract_status": "active",
            "risk_level": "low",
            "risk_summary": "Active contract and no compliance concerns.",
        }

    monkeypatch.setattr("agent.check_budget", fake_budget)
    monkeypatch.setattr("agent.check_vendor_duplication", fake_duplication)
    monkeypatch.setattr("agent.check_policy_compliance", fake_policy)
    monkeypatch.setattr("agent.assess_risk", fake_risk)

    recommendation = evaluate_request(request)

    assert recommendation.decision == "approve"
    assert calls == ["budget", "duplication", "policy", "risk"]


def test_precedence_escalate_over_deny(monkeypatch: pytest.MonkeyPatch) -> None:
    request = _sample_request()

    monkeypatch.setattr(
        "agent.check_budget",
        lambda *_: {
            "within_budget": False,
            "remaining_budget": 1000.0,
            "requested_amount": 5000.0,
            "overage": 4000.0,
            "cost_center_id": "CC-001",
        },
    )
    monkeypatch.setattr(
        "agent.check_vendor_duplication",
        lambda *_: {"violation": True, "reason": "POL-001 conflict"},
    )
    monkeypatch.setattr(
        "agent.check_policy_compliance",
        lambda *_: {
            "violations": [
                {
                    "policy_id": "POL-006",
                    "rule_description": "Compliance-flagged vendor",
                    "forced_decision": "escalate",
                }
            ],
            "violation_count": 1,
            "highest_severity": "escalate",
        },
    )
    monkeypatch.setattr(
        "agent.assess_risk",
        lambda *_: {
            "vendor_id": "V-006",
            "vendor_name": "Vertex",
            "compliance_flag": True,
            "compliance_notes": "Pending review",
            "contract_status": "active",
            "risk_level": "critical",
            "risk_summary": "Compliance flag requires escalation.",
        },
    )

    recommendation = evaluate_request(request)

    assert recommendation.decision == "escalate"
    assert "POL-006" in recommendation.rationale or "critical" in recommendation.rationale


def test_precedence_deny_over_approve(monkeypatch: pytest.MonkeyPatch) -> None:
    request = _sample_request()

    monkeypatch.setattr(
        "agent.check_budget",
        lambda *_: {
            "within_budget": False,
            "remaining_budget": 1000.0,
            "requested_amount": 5000.0,
            "overage": 4000.0,
            "cost_center_id": "CC-001",
        },
    )
    monkeypatch.setattr(
        "agent.check_vendor_duplication",
        lambda *_: {"violation": False, "reason": "No conflict"},
    )
    monkeypatch.setattr(
        "agent.check_policy_compliance",
        lambda *_: {"violations": [], "violation_count": 0, "highest_severity": "none"},
    )
    monkeypatch.setattr(
        "agent.assess_risk",
        lambda *_: {
            "vendor_id": "V-002",
            "vendor_name": "BlueSky",
            "compliance_flag": False,
            "compliance_notes": "",
            "contract_status": "active",
            "risk_level": "low",
            "risk_summary": "Low risk",
        },
    )

    recommendation = evaluate_request(request)

    assert recommendation.decision == "deny"
    assert "overage" in recommendation.rationale.lower()


def test_tool_error_triggers_safe_escalation(monkeypatch: pytest.MonkeyPatch) -> None:
    request = _sample_request()

    monkeypatch.setattr(
        "agent.check_budget",
        lambda *_: {
            "within_budget": True,
            "remaining_budget": 20000.0,
            "requested_amount": 5000.0,
            "overage": 0.0,
            "cost_center_id": "CC-001",
        },
    )
    monkeypatch.setattr(
        "agent.check_vendor_duplication",
        lambda *_: {
            "error": "Vendor dataset unavailable",
            "violation": False,
            "reason": "Unable to check",
        },
    )
    monkeypatch.setattr(
        "agent.check_policy_compliance",
        lambda *_: {"violations": [], "violation_count": 0, "highest_severity": "none"},
    )
    monkeypatch.setattr(
        "agent.assess_risk",
        lambda *_: {
            "vendor_id": "V-002",
            "vendor_name": "BlueSky",
            "compliance_flag": False,
            "compliance_notes": "",
            "contract_status": "active",
            "risk_level": "low",
            "risk_summary": "Low risk",
        },
    )

    recommendation = evaluate_request(request)

    assert recommendation.decision == "escalate"
    assert "error" in recommendation.rationale.lower()


def test_output_schema_enforces_allowed_decision_and_non_empty_rationale() -> None:
    with pytest.raises(ValueError):
        ProcurementRecommendation(
            request_id="REQ-OUT-1",
            decision="approve",
            rationale="   ",
        )


def test_integration_sample_requests_reach_all_decision_classes() -> None:
    requests_path = Path("mock_data") / "requests.json"
    raw_requests = json.loads(requests_path.read_text(encoding="utf-8"))

    outcomes: set[str] = set()
    for raw_request in raw_requests:
        payload = {k: v for k, v in raw_request.items() if k in PurchaseRequest.model_fields}
        recommendation = evaluate_request(PurchaseRequest(**payload))
        outcomes.add(recommendation.decision)
        assert recommendation.rationale.strip()

    assert {"approve", "deny", "escalate"}.issubset(outcomes)


def test_deny_rationale_references_driver(monkeypatch: pytest.MonkeyPatch) -> None:
    request = _sample_request()

    monkeypatch.setattr(
        "agent.check_budget",
        lambda *_: {
            "within_budget": True,
            "remaining_budget": 20000.0,
            "requested_amount": 5000.0,
            "overage": 0.0,
            "cost_center_id": "CC-001",
        },
    )
    monkeypatch.setattr(
        "agent.check_vendor_duplication",
        lambda *_: {"violation": True, "reason": "POL-001 threshold exceeded"},
    )
    monkeypatch.setattr(
        "agent.check_policy_compliance",
        lambda *_: {
            "violations": [
                {
                    "policy_id": "POL-001",
                    "rule_description": "Single-source restriction",
                    "forced_decision": "deny",
                }
            ],
            "violation_count": 1,
            "highest_severity": "deny",
        },
    )
    monkeypatch.setattr(
        "agent.assess_risk",
        lambda *_: {
            "vendor_id": "V-002",
            "vendor_name": "BlueSky",
            "compliance_flag": False,
            "compliance_notes": "",
            "contract_status": "active",
            "risk_level": "low",
            "risk_summary": "Low risk",
        },
    )

    recommendation = evaluate_request(request)

    assert recommendation.decision == "deny"
    assert "POL-001" in recommendation.rationale


def test_escalate_rationale_references_driver(monkeypatch: pytest.MonkeyPatch) -> None:
    request = _sample_request()

    monkeypatch.setattr(
        "agent.check_budget",
        lambda *_: {
            "within_budget": True,
            "remaining_budget": 20000.0,
            "requested_amount": 5000.0,
            "overage": 0.0,
            "cost_center_id": "CC-001",
        },
    )
    monkeypatch.setattr(
        "agent.check_vendor_duplication",
        lambda *_: {"violation": False, "reason": "No conflict"},
    )
    monkeypatch.setattr(
        "agent.check_policy_compliance",
        lambda *_: {
            "violations": [
                {
                    "policy_id": "POL-006",
                    "rule_description": "Compliance hold",
                    "forced_decision": "escalate",
                }
            ],
            "violation_count": 1,
            "highest_severity": "escalate",
        },
    )
    monkeypatch.setattr(
        "agent.assess_risk",
        lambda *_: {
            "vendor_id": "V-006",
            "vendor_name": "Vertex",
            "compliance_flag": True,
            "compliance_notes": "Pending ethics review",
            "contract_status": "active",
            "risk_level": "critical",
            "risk_summary": "Critical risk due to compliance flag.",
        },
    )

    recommendation = evaluate_request(request)

    assert recommendation.decision == "escalate"
    assert "POL-006" in recommendation.rationale or "critical" in recommendation.rationale