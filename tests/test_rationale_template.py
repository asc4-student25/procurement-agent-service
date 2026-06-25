"""Template-quality tests for recommendation rationale text."""

from __future__ import annotations

import re

from agent import evaluate_request
from data.loader import load_requests
from models import PurchaseRequest

_POLICY_ID_PATTERN = re.compile(r"\bPOL-\d{3}\b")
_MONEY_PATTERN = re.compile(r"\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?")
_SENTENCE_SPLIT_PATTERN = re.compile(r"(?<=[.!?])\s+")


def _sentence_count(text: str) -> int:
    """Count sentence-like segments in a rationale string."""
    parts = [segment.strip() for segment in _SENTENCE_SPLIT_PATTERN.split(text.strip())]
    return len([segment for segment in parts if segment])


def _check_names_driver(rationale: str) -> bool:
    """Validate rationale names one or more explicit checks."""
    lower = rationale.lower()
    check_terms = [
        "budget check",
        "vendor duplication check",
        "policy compliance check",
        "risk assessment",
        "tool error handling",
    ]
    return any(term in lower for term in check_terms)


def _has_required_context(rationale: str, vendor_name: str) -> bool:
    """Validate rationale includes amount, policy ID, or vendor context."""
    return bool(
        _MONEY_PATTERN.search(rationale)
        or _POLICY_ID_PATTERN.search(rationale)
        or vendor_name.lower() in rationale.lower()
    )


def _is_plain_prose(rationale: str) -> bool:
    """Reject bullet-list formatting in rationale text."""
    return "\n-" not in rationale and "\n*" not in rationale and "•" not in rationale


def test_all_sample_requests_meet_rationale_template() -> None:
    """All 15 sample requests should return template-compliant rationale text."""
    failures: list[str] = []

    for raw in load_requests():
        payload = {key: value for key, value in raw.items() if key in PurchaseRequest.model_fields}
        request = PurchaseRequest(**payload)
        recommendation = evaluate_request(request)
        rationale = recommendation.rationale.strip()
        sentence_count = _sentence_count(rationale)

        if not (2 <= sentence_count <= 4):
            failures.append(
                f"{request.request_id}: expected 2-4 sentences, got {sentence_count}"
            )
        if not _check_names_driver(rationale):
            failures.append(f"{request.request_id}: missing explicit decision-driving check")
        if not _has_required_context(rationale, request.vendor_name):
            failures.append(
                f"{request.request_id}: missing amount, policy ID, or vendor context"
            )
        if not _is_plain_prose(rationale):
            failures.append(f"{request.request_id}: rationale uses bullet formatting")

    assert not failures, "\n" + "\n".join(failures)
