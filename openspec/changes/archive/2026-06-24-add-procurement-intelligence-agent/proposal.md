# Proposal: Add Procurement Intelligence Agent

## Change ID

`add-procurement-intelligence-agent`

## Status

Proposed

## Summary

Add a procurement intelligence agent that evaluates purchase requests using four required checks
(budget, vendor duplication, policy compliance, and vendor risk) and returns a structured
recommendation of `approve`, `deny`, or `escalate` with a non-empty rationale.

The agent is advisory only. Final authority remains with human procurement officers.

## Why This Change

The procurement team processes a high volume of requests, many of which are routine. Manual
pre-screening creates avoidable latency and inconsistency in policy application. This change
introduces a reliable, explainable pre-screening layer that:

- reduces analyst effort on low-risk approvals,
- surfaces policy and contract violations early,
- routes ambiguous or high-risk requests for human escalation,
- preserves auditability through structured output and traceable rationale.

## Scope

This change includes:

- Typed input and output models for request and recommendation handling.
- A single mock-data access layer for budgets, vendors, policies, and sample requests.
- Four tool capabilities:
  - budget sufficiency check,
  - vendor duplication check (single-source policy threshold behavior),
  - policy compliance evaluation,
  - vendor risk assessment.
- Agent orchestration logic that runs all four checks for every request.
- Deterministic decision precedence across outcomes:
  - `escalate` takes precedence over `deny`,
  - `deny` takes precedence over `approve`.
- Error-aware fallback behavior that escalates when required data is unavailable.

## Out of Scope

- Automatic purchasing or contract execution.
- Replacing procurement officer decision authority.
- Editing reference fixtures in `mock_data/`.
- Live ERP, legal, or vendor management integrations.

## Story Traceability

This proposal addresses the following user stories in `user-stories.md`:

- US-001: budget screening before approval.
- US-002: vendor duplication detection in category context.
- US-003: full policy compliance evaluation.
- US-004: vendor risk and contract status assessment.
- US-005: structured recommendation with required rationale.

## Intended Capabilities

1. Validate and normalize purchase request input fields.
2. Produce schema-constrained recommendation output.
3. Evaluate budget against remaining cost-center funds.
4. Detect single-source conflicts using category and threshold logic.
5. Evaluate policy violations and return forced decision signals.
6. Assess vendor risk level from compliance and contract state.
7. Combine findings with strict decision priority and explicit rationale.
8. Expose tool/data failures in rationale and escalate safely.

## Acceptance Signals

The change is considered successful when all signals below are true:

- The agent accepts a purchase request and returns a structured recommendation object.
- Decision values are always one of `approve`, `deny`, or `escalate`.
- Rationale is always non-empty and references relevant checks/policies.
- All four checks run for each request (no short-circuiting).
- Tool failures do not crash execution; they produce escalation with error context.
- Test coverage includes approval, denial, policy-driven denial, and escalation paths.

## Session 1 Traceability Summary

The Session 1 domain exploration confirms that all required decision classes are represented
in sample request data and tied to explicit decision drivers:

- Approve anchor: REQ-001 (contracted vendor, in-budget spend, no policy violations).
- Deny anchor: REQ-006 (CC-003 budget overage; 11200 requested vs 6900 remaining).
- Escalate anchor: REQ-011 (V-006 compliance flag; POL-006 escalation trigger).

These anchors are used in spec and test planning so the implementation remains consistent
with the intended procurement decision model.

## Risks and Mitigations

- Risk: Ambiguous precedence when multiple checks disagree.
  - Mitigation: define explicit precedence (`escalate` > `deny` > `approve`) in spec and tests.
- Risk: Silent approval when data is missing.
  - Mitigation: require escalation if any tool or data dependency fails.
- Risk: Unclear rationale text reduces trust.
  - Mitigation: mandate rationale quality constraints and policy/check references.

## Implementation Impact

Impacted modules (expected):

- `models.py`
- `data/loader.py`
- `tools/budget.py`
- `tools/vendor_duplication.py`
- `tools/policy_compliance.py`
- `tools/risk_assessment.py`
- `agent.py`
- `tests/`

Impacted governance artifacts (expected):

- `openspec/changes/add-procurement-intelligence-agent/specs/` (delta specs)
- `openspec/changes/add-procurement-intelligence-agent/design.md`
- `openspec/changes/add-procurement-intelligence-agent/tasks.md`

## Validation Plan

- Author delta specs for all introduced capabilities.
- Validate the OpenSpec change using `openspec validate add-procurement-intelligence-agent`.
- Verify implementation behavior with automated tests and documented test results.

## OpenSpec Commands

Use the commands below for a strict spec-driven workflow:

```bash
# Validate only this change
openspec validate add-procurement-intelligence-agent

# Validate all changes in repository
openspec validate --all
```

```bash
# Run implementation test evidence for ITC.003
pytest tests/ -v --tb=short --junitxml=docs/test-results.xml
```

## OpenSpec Folder Details

This change uses the standard OpenSpec structure:

```text
openspec/
  changes/
    add-procurement-intelligence-agent/
      proposal.md
      design.md
      tasks.md
      specs/
        models/spec.md
        data-loader/spec.md
        budget-check/spec.md
        vendor-duplication/spec.md
        policy-compliance/spec.md
        risk-assessment/spec.md
        agent-orchestration/spec.md
```

Folder purpose:

- `proposal.md`: why the change exists, scope, impact, and acceptance signals.
- `design.md`: architecture and decision rules, including precedence and error fallback.
- `tasks.md`: ordered implementation checklist tied to tests and story IDs.
- `specs/*/spec.md`: measurable capability deltas and acceptance criteria.

## Spec-Driven Implementation Workflow

Implementation order for this change:

1. Write `proposal.md` and approve scope.
2. Write `design.md` for decision precedence and failure handling.
3. Write capability delta specs under `specs/`.
4. Run `openspec validate add-procurement-intelligence-agent`.
5. Implement code only after validation passes.
6. Execute tests and save XML evidence in `docs/test-results.xml`.
7. Update `tasks.md` status and prepare Go/No-Go evidence.
