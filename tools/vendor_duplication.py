"""Vendor duplication tool — checks for single-source policy violations (POL-001)."""

from __future__ import annotations

from data.loader import load_policies, load_vendors

# POL-001 threshold: single-source restriction applies above this amount
_POL001_THRESHOLD = 25_000.00
_POL001_AFFECTED_CATEGORIES = {
    "office_supplies",
    "software_licenses",
    "hardware",
    "facilities",
    "security",
    "fleet_parts",
    "staffing",
}


def _pol001_config() -> tuple[float, set[str]]:
    """Load POL-001 threshold and affected categories with safe defaults."""
    threshold = _POL001_THRESHOLD
    categories = set(_POL001_AFFECTED_CATEGORIES)

    policies = load_policies()
    policy = next((p for p in policies if p.get("policy_id") == "POL-001"), None)
    if not isinstance(policy, dict):
        return threshold, categories

    threshold_raw = policy.get("threshold_amount", threshold)
    try:
        threshold = float(threshold_raw)
    except (TypeError, ValueError):
        threshold = _POL001_THRESHOLD

    categories_raw = policy.get("affected_categories")
    if isinstance(categories_raw, list):
        parsed_categories = {
            str(value).strip() for value in categories_raw if str(value).strip()
        }
        if parsed_categories:
            categories = parsed_categories

    return threshold, categories


def check_vendor_duplication(
    vendor_id: str, category: str, amount: float
) -> dict[str, object]:
    """Detect single-source restriction violations per POL-001.

    Call this tool when the purchase category is one covered by the single-source
    restriction (office_supplies, software_licenses, hardware, facilities, security,
    fleet_parts, staffing). If the amount exceeds $25,000 and other vendors hold
    active contracts in the same category, this is a policy violation.

    Args:
        vendor_id: The vendor ID from the purchase request (e.g. "V-012").
        category: The purchase category (e.g. "office_supplies").
        amount: The total purchase amount in USD.

    Returns:
        A dict containing:
        - ``violation`` (bool): True if a single-source violation is detected.
        - ``vendor_id`` (str): The requested vendor.
        - ``category`` (str): The purchase category checked.
        - ``amount`` (float): The amount checked.
        - ``conflicting_vendor_ids`` (list[str]): Vendor IDs with active contracts in the same category.
        - ``conflicting_vendor_names`` (list[str]): Display names of conflicting vendors.
        - ``reason`` (str): Human-readable explanation of the result.
        - ``error`` (str, optional): Present only if vendor data could not be loaded.
    """
    try:
        vendors = load_vendors()
        threshold, covered_categories = _pol001_config()
    except (FileNotFoundError, ValueError) as exc:
        return {
            "error": f"Vendor data could not be loaded: {exc}",
            "violation": False,
            "vendor_id": vendor_id,
            "category": category,
            "amount": amount,
            "conflicting_vendor_ids": [],
            "conflicting_vendor_names": [],
            "reason": "Vendor data unavailable — could not perform duplication check.",
        }

    if category not in covered_categories:
        return {
            "violation": False,
            "vendor_id": vendor_id,
            "category": category,
            "amount": amount,
            "conflicting_vendor_ids": [],
            "conflicting_vendor_names": [],
            "reason": (
                f"Category '{category}' is not governed by POL-001 single-source restriction. "
                "No duplication violation."
            ),
        }

    if amount <= threshold:
        return {
            "violation": False,
            "vendor_id": vendor_id,
            "category": category,
            "amount": amount,
            "conflicting_vendor_ids": [],
            "conflicting_vendor_names": [],
            "reason": (
                f"Amount ${amount:,.2f} is at or below the ${threshold:,.2f} "
                "single-source restriction threshold. POL-001 does not apply."
            ),
        }

    # Find other vendors with active contracts in the same category.
    conflicts = [
        vendor
        for vendor in vendors
        if vendor.get("vendor_id") != vendor_id
        and vendor.get("category") == category
        and vendor.get("contract_status") == "active"
    ]

    if conflicts:
        names = [str(vendor.get("name", "Unknown")) for vendor in conflicts]
        ids = [str(vendor.get("vendor_id", "N/A")) for vendor in conflicts]
        return {
            "violation": True,
            "vendor_id": vendor_id,
            "category": category,
            "amount": amount,
            "conflicting_vendor_ids": ids,
            "conflicting_vendor_names": names,
            "reason": (
                f"POL-001 violation: amount ${amount:,.2f} exceeds the ${threshold:,.2f} "
                f"single-source threshold. Active contract vendor(s) for '{category}': "
                + ", ".join(f"{name} ({vendor_id_val})" for name, vendor_id_val in zip(names, ids))
                + ". Request must use a contracted vendor."
            ),
        }

    return {
        "violation": False,
        "vendor_id": vendor_id,
        "category": category,
        "amount": amount,
        "conflicting_vendor_ids": [],
        "conflicting_vendor_names": [],
        "reason": (
            f"No other active-contract vendors found for category '{category}'. "
            "No single-source violation."
        ),
    }
