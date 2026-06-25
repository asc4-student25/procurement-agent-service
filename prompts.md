# Prompt Log (AI-Assisted Development Evidence)

This file records the key prompts used to build the Procurement and Vendor Intelligence Agent.
It supports Category 5 grading and showcase prep.

## How to Use This File

- Keep one entry per meaningful prompt that produced or changed a key component.
- Add commit hash(es) that contain the resulting changes.
- Capture where the team accepted, redirected, or rejected AI output.
- Keep evidence specific and traceable to files and tests.

## Entry Template

### Prompt Entry: [short title]
- Date:
- Session:
- Story ID(s):
- Prompt goal:
- Prompt text:
- Output touched files:
- Team action: Accepted | Redirected | Rejected | Mixed
- Why this action was taken:
- Validation run:
- Commit(s):
- Notes for showcase:

---

## Suggested Baseline Entries (fill in your exact prompt text and commit hashes)

### Prompt Entry: Domain exploration and decision mapping
- Date: [fill in]
- Session: Session 1
- Story ID(s): US-001, US-002, US-003, US-004, US-005
- Prompt goal: Understand checks, decision rules, and edge cases from mock data before coding.
- Prompt text: @workspace Using /opsx-explore, analyze mock_data requests, policies, vendors, and budgets. Identify fields, checks, decision rules, and edge cases. Do not write code.
- Output touched files: openspec notes and planning artifacts
- Team action: Accepted
- Why this action was taken: The output aligned with policy IDs and request outcome patterns.
- Validation run: Team data walkthrough against mock_data files
- Commit(s): [fill in]
- Notes for showcase: Copilot accelerated initial domain understanding.

### Prompt Entry: OpenSpec proposal generation
- Date: [fill in]
- Session: Session 1
- Story ID(s): US-001, US-002, US-003, US-004, US-005
- Prompt goal: Generate proposal, design, tasks, and capability specs.
- Prompt text: /opsx-propose add-procurement-intelligence-agent [full scope description]
- Output touched files: openspec change artifacts and specs
- Team action: Redirected
- Why this action was taken: Team refined acceptance language and contracts to be measurable and aligned with policy behavior.
- Validation run: openspec validate [record output]
- Commit(s): [fill in]
- Notes for showcase: Example of redirecting AI output instead of accepting defaults.

### Prompt Entry: Models implementation
- Date: [fill in]
- Session: Session 2
- Story ID(s): US-005
- Prompt goal: Implement typed request and recommendation models.
- Prompt text: @workspace Implement models.py from spec with Pydantic v2; enforce decision literal and non-empty rationale.
- Output touched files: models.py
- Team action: Mixed
- Why this action was taken: Team accepted structure, then corrected field constraints and rationale validation strictness.
- Validation run: pytest tests/ -v
- Commit(s): [fill in]
- Notes for showcase: AI gave fast scaffold; humans tightened validation.

### Prompt Entry: Data loader implementation
- Date: [fill in]
- Session: Session 2
- Story ID(s): US-001
- Prompt goal: Centralize all mock data access in data loader.
- Prompt text: @workspace Create data/loader.py with load_budgets, load_vendors, load_policies, and load_requests using root-relative paths.
- Output touched files: data/loader.py
- Team action: Accepted
- Why this action was taken: Output matched architecture rule of no direct mock_data reads outside loader.
- Validation run: pytest tests/ -v
- Commit(s): [fill in]
- Notes for showcase: Direct productivity gain from boilerplate generation.

### Prompt Entry: Tool implementations and tests
- Date: [fill in]
- Session: Session 2-3
- Story ID(s): US-001, US-002, US-003, US-004
- Prompt goal: Build policy, vendor duplication, risk, and budget checks with tests.
- Prompt text: @workspace Implement tool from spec and add pytest coverage for success and edge cases.
- Output touched files: tools/* and tests/test_*.py
- Team action: Mixed
- Why this action was taken: Team corrected threshold behavior and policy forcing logic where AI was ambiguous.
- Validation run: pytest tests/ -v --tb=short --junitxml=docs/test-results.xml
- Commit(s): [fill in]
- Notes for showcase: Clear example where human policy interpretation corrected generated code.

### Prompt Entry: Agent orchestration and rationale quality
- Date: [fill in]
- Session: Session 3-4
- Story ID(s): US-005
- Prompt goal: Wire four checks and enforce precedence escalate > deny > approve with concrete rationale.
- Prompt text: @workspace Implement agent.py with structured output_type, all tools, and explicit decision precedence.
- Output touched files: agent.py, tests/test_agent.py
- Team action: Redirected
- Why this action was taken: Team rejected vague rationale language and required explicit policy IDs and risk drivers.
- Validation run: pytest tests/ -v
- Commit(s): [fill in]
- Notes for showcase: Best example of tightening system prompt and output quality.

---

## Showcase Evidence Snippets

### 1) One place we redirected or rejected Copilot output, and why
- Example: Team rejected initial policy compliance logic because it treated manager approval guidance as an automatic deny. It was changed to escalation-only behavior aligned to policy intent.

### 2) Where Copilot helped us move faster
- Example: Rapid generation of Pydantic model and loader scaffolding reduced setup time and let the team focus on policy edge cases.

### 3) Where humans had to step in and correct AI
- Example: Team corrected precedence and rationale detail requirements to ensure escalation wins over deny and outputs are audit-ready.

---

## Traceability Checklist

- Prompt entries map to US-001 through US-005.
- Entries include commit hashes.
- Entries include at least one Redirected or Rejected case.
- Entries include at least one speedup case.
- Entries include at least one human correction case.
- Validation commands and outcomes are captured.
