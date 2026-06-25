# Tasks: Add Procurement Intelligence Agent

## Spec-Driven Task List

- [x] Create proposal: `proposal.md`
- [x] Create architecture design: `design.md`
- [x] Author capability specs under `specs/`
- [x] Add implementation guardrails: `guardrails.md`
- [ ] Run OpenSpec validation for this change
- [ ] Align implementation to approved specs
- [ ] Execute tests and capture XML evidence
- [ ] Complete Go/No-Go checklist evidence fields

## Implementation Progress Checkpoints

- [x] Member 1 (US-001) implementation aligned to specs
	- Updated loader validation behavior in `solutions/data/loader.py`.
	- Updated budget fallback, malformed-record handling, and fixture key handling in `tools/budget.py`.
	- Added/updated US-001 tests in `tests/test_budget.py` and `tests/test_loader.py`.
- [x] Member 1 (US-001) test evidence captured
	- Ran `pytest tests/test_budget.py tests/test_loader.py -v --tb=short --junitxml=docs/test-results.xml` from project root.
	- Evidence file generated: `docs/test-results.xml` (11 passed, 0 failed).
- [ ] Full change alignment complete across US-001 through US-005
- [ ] Full-suite XML evidence captured using project standard command

## Capability Spec Authoring Tasks

- [x] `specs/models/spec.md`
- [x] `specs/data-loader/spec.md`
- [x] `specs/budget-check/spec.md`
- [x] `specs/vendor-duplication/spec.md`
- [x] `specs/policy-compliance/spec.md`
- [x] `specs/risk-assessment/spec.md`
- [x] `specs/agent-orchestration/spec.md`

## Session 1 Outcome Traceability

- [x] Identify one sample request expected to approve and document why
	- REQ-001 expected approve: active contracted vendor V-002, amount 24000 within CC-001 remaining 187550, no policy violation.
- [x] Identify one sample request expected to deny and document why
	- REQ-006 expected deny: amount 11200 exceeds CC-003 remaining 6900 (overage 4300), budget overage prohibition behavior.
- [x] Identify one sample request expected to escalate and document why
	- REQ-011 expected escalate: vendor V-006 is compliance-flagged, triggering POL-006 escalation.
- [x] Confirm rationale drivers map to at least one check or policy per outcome
	- Approve driver: clean budget, policy, duplication, and risk checks (REQ-001).
	- Deny driver: budget-check overage result and policy budget prohibition behavior (REQ-006).
	- Escalate driver: policy-compliance and risk checks for compliance-flagged vendor (REQ-011).
- [x] Confirm budget-check behavior is explicitly represented in Session 1 notes
	- Budget edge case anchored on CC-003 remaining 6900 with REQ-006 overage calculation.

## Validation and Evidence Commands

```bash
openspec validate add-procurement-intelligence-agent
openspec validate --all
pytest tests/ -v --tb=short --junitxml=docs/test-results.xml
```

## Completion Criteria

- All capability specs exist and have measurable acceptance criteria.
- `openspec validate add-procurement-intelligence-agent` passes.
- Tests pass with evidence committed in `docs/test-results.xml`.
- Commit messages include applicable user story IDs.
