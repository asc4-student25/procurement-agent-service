"""Pytest-asyncio suite for required procurement agent decision cases."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from agent import evaluate_request
from data.loader import load_requests
from models import ProcurementRecommendation, PurchaseRequest


@dataclass(slots=True)
class _ResultWrapper:
    """Mirror the pydantic-ai result shape used by acceptance assertions."""

    data: ProcurementRecommendation


def _request_from_mock(request_id: str) -> PurchaseRequest:
    """Return a typed purchase request from mock_data/requests.json by request_id."""
    raw = next(
        (item for item in load_requests() if item.get("request_id") == request_id),
        None,
    )
    if raw is None:
        raise ValueError(f"Unknown request id in test fixture: {request_id}")

    payload = {k: v for k, v in raw.items() if k in PurchaseRequest.model_fields}
    return PurchaseRequest(**payload)


def _raw_request_from_mock(request_id: str) -> dict[str, object]:
    """Return a raw request fixture row by request_id."""
    raw = next(
        (item for item in load_requests() if item.get("request_id") == request_id),
        None,
    )
    if raw is None:
        raise ValueError(f"Unknown request id in test fixture: {request_id}")
    return raw


async def _run_request(request_id: str) -> _ResultWrapper:
    """Evaluate a fixture request and expose output as result.data."""
    recommendation = evaluate_request(_request_from_mock(request_id))
    return _ResultWrapper(data=recommendation)


def _assert_non_empty_rationale(result: _ResultWrapper) -> None:
    """Assert rationale is a non-empty string."""
    assert isinstance(result.data.rationale, str)
    assert result.data.rationale.strip() != ""


@pytest.mark.asyncio
async def test_approve_req_001() -> None:
    result = await _run_request("REQ-001")

    assert result.data.decision == "approve"
    _assert_non_empty_rationale(result)


@pytest.mark.asyncio
async def test_deny_req_006_budget_overage() -> None:
    result = await _run_request("REQ-006")

    assert result.data.decision == "deny"
    _assert_non_empty_rationale(result)


@pytest.mark.asyncio
async def test_policy_deny_req_009_catering_prohibition() -> None:
    result = await _run_request("REQ-009")

    assert result.data.decision == "deny"
    _assert_non_empty_rationale(result)


@pytest.mark.asyncio
async def test_escalate_req_011_compliance_flagged_vendor() -> None:
    result = await _run_request("REQ-011")

    assert result.data.decision == "escalate"
    _assert_non_empty_rationale(result)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_id",
    [
        "REQ-006",
        "REQ-007",
        "REQ-008",
        "REQ-009",
        "REQ-010",
        "REQ-011",
        "REQ-001",
        "REQ-002",
        "REQ-003",
    ],
)
async def test_parametrized_expected_outcome_matches_decision(request_id: str) -> None:
    raw = _raw_request_from_mock(request_id)
    expected_outcome = raw.get("expected_outcome")
    if not isinstance(expected_outcome, str):
        raise ValueError(f"Fixture {request_id} missing string expected_outcome")

    result = await _run_request(request_id)

    assert result.data.decision == expected_outcome
