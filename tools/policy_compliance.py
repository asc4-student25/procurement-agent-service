"""Policy compliance tool — evaluates a purchase request against all eight policies."""

from __future__ import annotations

from data.loader import load_budgets, load_policies, load_vendors

# Amount within this fraction of the director threshold triggers near-threshold escalation.
_DIRECTOR_THRESHOLD = 50_000.00
_NEAR_THRESHOLD_FRACTION = 0.05
_MANAGER_THRESHOLD_LOW = 10_000.00
_MANAGER_THRESHOLD_HIGH = 49_999.99
_POL001_DEFAULT_THRESHOLD = 25_000.00
_POL001_DEFAULT_AFFECTED_CATEGORIES = {
    "office_supplies",
    "software_licenses",
    "hardware",
    "facilities",
    "security",
    "fleet_parts",
    "staffing",
}


def _find_policy(
    policies: list[dict[str, object]], policy_id: str
) -> dict[str, object] | None:
    """Return a policy record by ID when available."""
    return next(
        (
            policy
            for policy in policies
            if isinstance(policy, dict) and policy.get("policy_id") == policy_id
        ),
        None,
    )


def _policy_threshold(policy: dict[str, object] | None, default: float) -> float:
    """Parse threshold amount with fallback to a deterministic default."""
    if policy is None:
        return default
    raw = policy.get("threshold_amount", default)
    try:
        return float(raw)
    except (TypeError, ValueError):
        return default


def _highest_severity(violations: list[dict[str, str]]) -> str:
    """Resolve output severity with explicit escalate-over-deny precedence."""
    decisions = {violation["forced_decision"] for violation in violations}
    if "escalate" in decisions:
        return "escalate"
    if "deny" in decisions:
        return "deny"
    return "none"


def _pol001_context(policies: list[dict[str, object]]) -> tuple[float, set[str]]:
    """Return POL-001 threshold and category coverage with safe defaults."""
    policy = _find_policy(policies, "POL-001")
    threshold = _policy_threshold(policy, _POL001_DEFAULT_THRESHOLD)
    categories = set(_POL001_DEFAULT_AFFECTED_CATEGORIES)

    if policy is not None:
        affected_raw = policy.get("affected_categories")
        if isinstance(affected_raw, list):
            parsed_categories = {
                str(value).strip() for value in affected_raw if str(value).strip()
            }
            if parsed_categories:
                categories = parsed_categories

    return threshold, categories


def check_policy_compliance(
    vendor_id: str,
    category: str,
    amount: float,
    quantity: int = 0,
    manager_approval_present: bool | None = None,
    cost_center_id: str | None = None,
) -> dict[str, object]:
    """Evaluate a purchase request against procurement policies.

    Args:
        vendor_id: The vendor ID from the purchase request.
        category: The purchase category.
        amount: The total purchase amount in USD.
        quantity: The number of units (used for staffing hour-based checks).
        manager_approval_present: Optional signal for POL-002. Set to ``False``
            when required manager approval is missing.
        cost_center_id: Optional cost center ID used to evaluate POL-008.

    Returns:
        A dict containing ``violations``, ``violation_count``, and ``highest_severity``.
    """
    try:
        vendors = load_vendors()
        policies = load_policies()
        budgets = load_budgets() if cost_center_id else []
    except (FileNotFoundError, ValueError) as exc:
        return {
            "error": f"Policy or vendor data could not be loaded: {exc}",
            "violations": [],
            "violation_count": 0,
            "highest_severity": "escalate",
        }

    vendor = next((record for record in vendors if record.get("vendor_id") == vendor_id), None)
    violations: list[dict[str, str]] = []

    pol001_threshold, pol001_categories = _pol001_context(policies)
    pol002_threshold = _policy_threshold(_find_policy(policies, "POL-002"), _MANAGER_THRESHOLD_LOW)
    pol003_threshold = _policy_threshold(_find_policy(policies, "POL-003"), _DIRECTOR_THRESHOLD)

    # POL-001: Single-source restriction above threshold for covered categories.
    if category in pol001_categories and amount > pol001_threshold:
        conflicts = [
            candidate
            for candidate in vendors
            if candidate.get("vendor_id") != vendor_id
            and candidate.get("category") == category
            and candidate.get("contract_status") == "active"
        ]
        if conflicts:
            conflict_details = ", ".join(
                f"{candidate.get('name', 'Unknown')} ({candidate.get('vendor_id', 'N/A')})"
                for candidate in conflicts
            )
            violations.append({
                "policy_id": "POL-001",
                "rule_description": (
                    f"Amount ${amount:,.2f} exceeds the POL-001 threshold of "
                    f"${pol001_threshold:,.2f} for '{category}', and active contracted "
                    f"vendor(s) already exist: {conflict_details}."
                ),
                "forced_decision": "deny",
            })

    # POL-002: Manager approval required when explicit evidence says it is missing.
    if (
        pol002_threshold <= amount <= _MANAGER_THRESHOLD_HIGH
        and manager_approval_present is False
    ):
        violations.append({
            "policy_id": "POL-002",
            "rule_description": (
                f"Purchase amount ${amount:,.2f} is within the manager approval band "
                f"(${pol002_threshold:,.2f} to ${_MANAGER_THRESHOLD_HIGH:,.2f}) and "
                "manager approval is missing."
            ),
            "forced_decision": "escalate",
        })

    # POL-003: Director threshold and near-threshold escalation.
    if amount >= pol003_threshold:
        violations.append({
            "policy_id": "POL-003",
            "rule_description": (
                f"Purchase amount ${amount:,.2f} meets or exceeds the director approval "
                f"threshold of ${pol003_threshold:,.2f}. Director-level sign-off required."
            ),
            "forced_decision": "escalate",
        })
    elif amount >= pol003_threshold * (1 - _NEAR_THRESHOLD_FRACTION):
        violations.append({
            "policy_id": "POL-003",
            "rule_description": (
                f"Purchase amount ${amount:,.2f} is within 5% of the director approval "
                f"threshold (${pol003_threshold:,.2f}). Escalation recommended to ensure "
                "director awareness before commitment."
            ),
            "forced_decision": "escalate",
        })

    # POL-004: Catering prohibition.
    if category == "catering":
        violations.append({
            "policy_id": "POL-004",
            "rule_description": (
                "Catering and food service purchases are prohibited under the Q4 2025 "
                "corporate spend reduction initiative. Denied regardless of amount."
            ),
            "forced_decision": "deny",
        })

    # POL-005: Expired contract vendor.
    if vendor and vendor.get("contract_status") == "expired":
        violations.append({
            "policy_id": "POL-005",
            "rule_description": (
                f"Vendor {vendor.get('name', 'Unknown')} ({vendor_id}) has an expired contract "
                f"({vendor.get('contract_id', 'unknown')}). Purchases may not proceed until "
                "the contract is renewed."
            ),
            "forced_decision": "deny",
        })

    # POL-006: Compliance-flagged vendor.
    if vendor and vendor.get("compliance_flag") is True:
        notes = str(vendor.get("compliance_notes", "No details available."))
        violations.append({
            "policy_id": "POL-006",
            "rule_description": (
                f"Vendor {vendor.get('name', 'Unknown')} ({vendor_id}) has an active compliance "
                f"flag. Notes: {notes} All purchases from flagged vendors must be escalated to "
                "Legal and Compliance before approval."
            ),
            "forced_decision": "escalate",
        })

    # POL-007: Staffing non-contracted vendor (>40 hours).
    if category == "staffing" and quantity > 40:
        if not vendor or vendor.get("contract_status") != "active":
            violations.append({
                "policy_id": "POL-007",
                "rule_description": (
                    f"Staffing engagement of {quantity} hours exceeds 40-hour threshold. "
                    "All contingent staffing engagements must use the enterprise staffing "
                    "contract. This vendor does not hold an active staffing contract."
                ),
                "forced_decision": "deny",
            })

    # POL-008: Budget overage prohibition (with cost center context).
    if cost_center_id:
        center = next(
            (
                record
                for record in budgets
                if isinstance(record, dict) and record.get("cost_center_id") == cost_center_id
            ),
            None,
        )
        if center is not None:
            remaining_raw = center.get("remaining", center.get("remaining_budget", 0.0))
            try:
                remaining = float(remaining_raw)
            except (TypeError, ValueError):
                remaining = 0.0
            if amount > remaining:
                overage = amount - remaining
                violations.append({
                    "policy_id": "POL-008",
                    "rule_description": (
                        f"Request exceeds remaining budget for {cost_center_id} by "
                        f"${overage:,.2f} (remaining ${remaining:,.2f}, requested ${amount:,.2f})."
                    ),
                    "forced_decision": "deny",
                })

    return {
        "violations": violations,
        "violation_count": len(violations),
        "highest_severity": _highest_severity(violations),
    }
