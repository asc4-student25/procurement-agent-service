"""Main orchestration for procurement recommendation synthesis."""

from __future__ import annotations

import os
from typing import Literal

from dotenv import load_dotenv
from pydantic_ai import Agent

from models import ProcurementRecommendation, PurchaseRequest

try:
    from tools.budget import check_budget
except ImportError:  # pragma: no cover - temporary fallback while repo is being aligned
    from solutions.tools.budget import check_budget

try:
    from tools.vendor_duplication import check_vendor_duplication
except ImportError:  # pragma: no cover - temporary fallback while repo is being aligned
    from solutions.tools.vendor_duplication import check_vendor_duplication

try:
    from tools.policy_compliance import check_policy_compliance
except ImportError:  # pragma: no cover - temporary fallback while repo is being aligned
    from solutions.tools.policy_compliance import check_policy_compliance

from tools.risk_assessment import assess_risk

load_dotenv()

Decision = Literal["approve", "deny", "escalate"]

_SYSTEM_PROMPT = """
You are the FedEx Procurement Intelligence Agent.

Always run all four checks for each request:
1) budget check
2) vendor duplication check
3) policy compliance check
4) risk assessment

Apply deterministic decision precedence:
- escalate has highest precedence
- deny has next precedence
- approve is only allowed when no escalate/deny drivers are present

Escalate if any check returns an error payload or any escalation driver appears.
Rationale must reference concrete findings (policy IDs, overage amounts, risk level, or tool errors).
"""


def _extract_errors(*results: dict[str, object]) -> list[str]:
    """Collect non-empty tool error messages."""
    errors: list[str] = []
    for result in results:
        error = result.get("error")
        if isinstance(error, str) and error.strip():
            errors.append(error.strip())
    return errors


def _derive_decision(
    budget_result: dict[str, object],
    duplication_result: dict[str, object],
    policy_result: dict[str, object],
    risk_result: dict[str, object],
) -> Decision:
    """Enforce decision precedence: escalate > deny > approve."""
    errors = _extract_errors(budget_result, duplication_result, policy_result, risk_result)

    escalate = any(
        [
            bool(errors),
            str(policy_result.get("highest_severity", "none")) == "escalate",
            str(risk_result.get("risk_level", "")) == "critical",
        ]
    )
    if escalate:
        return "escalate"

    deny = any(
        [
            not bool(budget_result.get("within_budget", True)),
            bool(duplication_result.get("violation", False)),
            str(policy_result.get("highest_severity", "none")) == "deny",
            str(risk_result.get("risk_level", "")) == "high",
        ]
    )
    if deny:
        return "deny"

    return "approve"


def _build_rationale(
    request: PurchaseRequest,
    decision: Decision,
    budget_result: dict[str, object],
    duplication_result: dict[str, object],
    policy_result: dict[str, object],
    risk_result: dict[str, object],
) -> str:
    """Compose traceable rationale with concrete drivers from each check."""
    fragments: list[str] = []

    remaining = float(budget_result.get("remaining_budget", 0.0) or 0.0)
    overage = float(budget_result.get("overage", 0.0) or 0.0)
    if overage > 0:
        fragments.append(
            (
                f"Budget check for {request.cost_center_id} found a ${overage:,.2f} overage "
                f"on ${request.total_amount:,.2f} with ${remaining:,.2f} remaining."
            )
        )
    else:
        fragments.append(
            (
                f"Budget check for {request.cost_center_id} passed with ${remaining:,.2f} "
                f"remaining after a ${request.total_amount:,.2f} request."
            )
        )

    if bool(duplication_result.get("violation", False)):
        fragments.append(f"Vendor duplication check flagged POL-001 risk: {duplication_result.get('reason', '')}")
    else:
        fragments.append("Vendor duplication check found no single-source conflict.")

    violations = policy_result.get("violations", [])
    if isinstance(violations, list) and violations:
        policy_ids = [
            str(v.get("policy_id"))
            for v in violations
            if isinstance(v, dict) and v.get("policy_id")
        ]
        if policy_ids:
            fragments.append(f"Policy compliance identified: {', '.join(policy_ids)}.")
    else:
        fragments.append("Policy compliance check reported no violations.")

    risk_level = str(risk_result.get("risk_level", "unknown"))
    risk_summary = str(risk_result.get("risk_summary", "No risk summary available.")).strip()
    fragments.append(f"Risk assessment returned {risk_level} risk: {risk_summary}")

    errors = _extract_errors(budget_result, duplication_result, policy_result, risk_result)
    if errors:
        fragments.append("Tool errors required safe fallback escalation: " + " | ".join(errors))

    fragments.append(f"Final recommendation: {decision} (precedence: escalate > deny > approve).")

    return " ".join(fragment for fragment in fragments if fragment.strip())


def evaluate_request(request: PurchaseRequest) -> ProcurementRecommendation:
    """Run all checks and synthesize a schema-valid recommendation."""
    budget_result = check_budget(request.cost_center_id, request.total_amount)
    duplication_result = check_vendor_duplication(
        request.vendor_id,
        request.category,
        request.total_amount,
    )
    policy_result = check_policy_compliance(
        request.vendor_id,
        request.category,
        request.total_amount,
        request.quantity,
    )
    risk_result = assess_risk(request.vendor_id)

    decision = _derive_decision(
        budget_result=budget_result,
        duplication_result=duplication_result,
        policy_result=policy_result,
        risk_result=risk_result,
    )
    rationale = _build_rationale(
        request=request,
        decision=decision,
        budget_result=budget_result,
        duplication_result=duplication_result,
        policy_result=policy_result,
        risk_result=risk_result,
    )

    return ProcurementRecommendation(
        request_id=request.request_id,
        decision=decision,
        rationale=rationale,
    )


agent: Agent[None, ProcurementRecommendation] = Agent(
    model=os.getenv("PROCUREMENT_AGENT_MODEL", "anthropic:claude-3-5-haiku-latest"),
    output_type=ProcurementRecommendation,
    system_prompt=_SYSTEM_PROMPT,
    tools=[check_budget, check_vendor_duplication, check_policy_compliance, assess_risk],
)