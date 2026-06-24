"""Pydantic models for procurement agent input/output contracts."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PurchaseRequest(BaseModel):
    """Structured purchase request evaluated by the procurement agent."""

    model_config = ConfigDict(str_strip_whitespace=True)

    request_id: str = Field(description="Unique request identifier")
    requestor: str = Field(description="Name of the employee submitting the request")
    cost_center_id: str = Field(description="Cost center identifier")
    vendor_name: str = Field(description="Vendor display name")
    vendor_id: str = Field(description="Vendor identifier")
    category: str = Field(description="Purchase category")
    item_description: str = Field(description="What is being purchased")
    quantity: int = Field(gt=0, description="Number of units")
    unit_price: float = Field(gt=0, description="Price per unit")
    total_amount: float = Field(gt=0, description="Total request amount")


class ProcurementRecommendation(BaseModel):
    """Structured recommendation returned by the procurement agent."""

    model_config = ConfigDict(str_strip_whitespace=True)

    request_id: str = Field(description="Request identifier")
    decision: Literal["approve", "deny", "escalate"] = Field(
        description="Agent recommendation outcome"
    )
    rationale: str = Field(
        description="Non-empty rationale referencing concrete drivers from checks"
    )

    @field_validator("rationale")
    @classmethod
    def rationale_non_empty(cls, value: str) -> str:
        """Enforce non-empty, meaningful rationale text."""
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("rationale must be non-empty")
        if len(trimmed) < 20:
            raise ValueError("rationale must include meaningful decision context")
        return trimmed