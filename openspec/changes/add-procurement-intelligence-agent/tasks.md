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

## Capability Spec Authoring Tasks

- [x] `specs/models/spec.md`
- [x] `specs/data-loader/spec.md`
- [x] `specs/budget-check/spec.md`
- [x] `specs/vendor-duplication/spec.md`
- [x] `specs/policy-compliance/spec.md`
- [x] `specs/risk-assessment/spec.md`
- [x] `specs/agent-orchestration/spec.md`

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
