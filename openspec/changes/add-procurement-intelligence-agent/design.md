# Design: Add Procurement Intelligence Agent

## Purpose

Define architecture and decision rules for a spec-driven procurement recommendation agent.

## Design Goals

- Enforce deterministic outcomes: `escalate` > `deny` > `approve`.
- Ensure all four checks execute for each request.
- Keep structured, typed input/output contracts.
- Fail safely by escalating on tool/data errors.
- Keep rationale explicit and traceable to checks and policy IDs.

## System Components

- `models.py`: `PurchaseRequest`, `ProcurementRecommendation`
- `data/loader.py`: single access layer for all `mock_data/*.json`
- `tools/budget.py`: budget sufficiency and overage
- `tools/vendor_duplication.py`: POL-001 threshold and active-contract conflict detection
- `tools/policy_compliance.py`: policy violation detection and forced decisions
- `tools/risk_assessment.py`: vendor risk profile (`low|medium|high|critical`)
- `agent.py`: orchestration and final decision synthesis

## Data Flow

1. Validate request payload against `PurchaseRequest`.
2. Run budget, duplication, policy, and risk checks.
3. Capture tool outputs, including error fields.
4. Apply decision precedence based on findings.
5. Emit `ProcurementRecommendation` with non-empty rationale.

## Decision Arbitration

Priority order:

1. `escalate`
2. `deny`
3. `approve`

Escalate triggers include:

- Any tool/data error.
- Critical risk from compliance-flagged vendor.
- Policy violations requiring escalation.
- Director-threshold and near-threshold policy escalation rules.

Deny triggers include (when no escalate trigger exists):

- Budget overage.
- Single-source violation above policy threshold.
- Policy violations forcing denial.
- High risk caused by expired contract.

Approve condition:

- All checks completed successfully and no deny/escalate triggers are present.

## Error Handling

- Tool functions return structured error context using an `error` key.
- The agent never silently ignores tool errors.
- If any check cannot be trusted due to missing data, final decision is `escalate`.

## Testing Strategy

- Unit tests for each tool success path and key edge cases.
- Integration tests for at least one `approve`, `deny`, and `escalate` scenario.
- Test evidence captured via `docs/test-results.xml`.

## Open Questions

- Whether integration tests should always use mocked model backend to avoid live API dependency.
- Whether additional policy IDs (e.g., POL-008 references) should be standardized in specs.
