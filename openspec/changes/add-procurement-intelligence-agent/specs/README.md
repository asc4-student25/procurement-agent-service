# Specs Folder Guide

This folder contains capability delta specs for the
`add-procurement-intelligence-agent` change.

## Required Spec Files

Create one folder per capability, each with a `spec.md` file:

- `models/spec.md`
- `data-loader/spec.md`
- `budget-check/spec.md`
- `vendor-duplication/spec.md`
- `policy-compliance/spec.md`
- `risk-assessment/spec.md`
- `agent-orchestration/spec.md`

## Authoring Rules

- Every requirement must be measurable and testable.
- Include expected behavior for success, edge, and failure paths.
- Explicitly define outcome precedence (`escalate` > `deny` > `approve`).
- Include rationale quality expectations in orchestration spec.
- Keep IDs and policy references consistent with `mock_data/policies.json`.

## Validation

Run:

```bash
openspec validate add-procurement-intelligence-agent
```
