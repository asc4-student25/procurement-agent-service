"""Tests for error handling paths required by acceptance criteria."""

from __future__ import annotations

from unittest.mock import patch

from agent import evaluate_request
from models import PurchaseRequest


def _sample_request(*, vendor_id: str = "V-002") -> PurchaseRequest:
    """Build a valid request payload for error-path tests."""
    return PurchaseRequest(
        request_id="REQ-ERR-001",
        requestor="Test User",
        cost_center_id="CC-001",
        vendor_name="BlueSky Cloud Solutions",
        vendor_id=vendor_id,
        category="software_licenses",
        item_description="Error-path validation purchase",
        quantity=1,
        unit_price=1000.0,
        total_amount=1000.0,
    )


def test_budget_loader_runtime_error_returns_recommendation_with_failure_rationale() -> None:
    """Tool RuntimeError should be captured and surfaced in decision rationale."""
    request = _sample_request(vendor_id="V-002")

    with patch("data.loader.load_budgets", side_effect=RuntimeError("simulated budget outage")):
        recommendation = evaluate_request(request)

    assert recommendation.request_id == request.request_id
    assert recommendation.decision == "escalate"
    assert recommendation.rationale.strip() != ""
    assert "tool" in recommendation.rationale.lower() or "failure" in recommendation.rationale.lower()
    assert "simulated budget outage" in recommendation.rationale


def test_unknown_vendor_id_escalates_with_unknown_vendor_rationale() -> None:
    """Unknown vendor should not crash and must escalate with explicit rationale context."""
    request = _sample_request(vendor_id="V-999")

    recommendation = evaluate_request(request)

    assert recommendation.request_id == request.request_id
    assert recommendation.decision == "escalate"
    assert recommendation.rationale.strip() != ""
    assert "vendor" in recommendation.rationale.lower()
    assert "not found" in recommendation.rationale.lower() or "unknown" in recommendation.rationale.lower()
