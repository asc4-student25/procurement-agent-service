"""Main orchestration for procurement recommendation synthesis."""

from __future__ import annotations

import os
from typing import Literal

from dotenv import load_dotenv
from pydantic_ai import Agent

from models import ProcurementRecommendation, PurchaseRequest
from tools.budget import check_budget
from tools.policy_compliance import check_policy_compliance
from tools.risk_assessment import assess_risk
from tools.vendor_duplication import check_vendor_duplication

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

Hard rule for tool failures:
- If any tool response contains an error field, the final decision is always escalate.
- Include the tool error message explicitly in the rationale.

Escalation drivers:
- Escalate for critical risk findings.
- Escalate if the request amount is within 5% of the director approval threshold.

Rationale template requirements (strict):
- Write 2 to 4 complete sentences in plain prose (no bullet points).
- Name the specific check(s) that drove the decision.
- Include concrete context such as policy IDs, amounts, vendor names, risk levels, or tool errors.
- End with a sentence that states the final recommendation.
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
    """Compose a concise rationale with explicit drivers and concrete context."""
    request_amount = float(request.total_amount)
    remaining = float(budget_result.get("remaining_budget", 0.0) or 0.0)
    overage = float(budget_result.get("overage", 0.0) or 0.0)
    risk_level = str(risk_result.get("risk_level", "unknown"))
    errors = _extract_errors(budget_result, duplication_result, policy_result, risk_result)

    violations = policy_result.get("violations", [])
    policy_ids = [
        str(v.get("policy_id"))
        for v in violations
        if isinstance(v, dict) and v.get("policy_id")
    ]

    active_drivers: list[str] = []
    if errors:
        active_drivers.append("tool error handling")
    if overage > 0:
        active_drivers.append("budget check")
    if bool(duplication_result.get("violation", False)):
        active_drivers.append("vendor duplication check")
    if policy_ids:
        active_drivers.append("policy compliance check")
    if risk_level in {"high", "critical"}:
        active_drivers.append("risk assessment")

    if not active_drivers:
        active_drivers = ["budget check", "policy compliance check", "risk assessment"]

    if len(active_drivers) == 1:
        checks_phrase = active_drivers[0]
    elif len(active_drivers) == 2:
        checks_phrase = f"{active_drivers[0]} and {active_drivers[1]}"
    else:
        checks_phrase = ", ".join(active_drivers[:-1]) + f", and {active_drivers[-1]}"

    sentence_1 = (
        f"The {checks_phrase} drove this decision for request {request.request_id} from "
        f"{request.vendor_name}."
    )

    details: list[str] = [
        (
            f"The request amount is ${request_amount:,.2f} for cost center {request.cost_center_id}, "
            f"with ${remaining:,.2f} remaining"
        )
    ]
    if overage > 0:
        details.append(f"an overage of ${overage:,.2f}")
    if policy_ids:
        details.append(f"policy findings {', '.join(policy_ids)}")
    details.append(f"risk level {risk_level}")
    if errors:
        details.append(f"tool errors: {' | '.join(errors)}")

    sentence_2 = "; ".join(details) + "."
    sentence_3 = f"Final recommendation: {decision}."

    return " ".join([sentence_1, sentence_2, sentence_3])


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