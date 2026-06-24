# Guardrails: Spec-Driven Implementation

## Purpose

These guardrails define how implementation must follow approved specs in this change.

## Process Guardrails

1. Do not implement or modify agent, tools, or models before corresponding spec files exist.
2. Do not mark tasks complete until both tests and OpenSpec validation pass.
3. Run `openspec validate add-procurement-intelligence-agent` before raising code review.
4. Keep proposal, design, tasks, and capability specs synchronized after each scope change.

## SDD Workflow Commands

Agent mode commands (Copilot chat):

1. `/opsx-explore` to inspect data shapes, edge cases, and decision rules.
2. `/opsx-propose <change-name>` to draft proposal and formal spec artifacts.
3. `/opsx-continue` to advance to the next artifact in the current change.

CLI commands (terminal):

1. `openspec validate add-procurement-intelligence-agent` to validate this change.
2. `openspec validate --all` to validate all repository changes.
3. `openspec list` to list change folders and status.

## Scope Guardrails

1. Do not modify files in mock_data.
2. Do not change dependency manifest unless explicitly requested.
3. Keep implementation inside established project structure.
4. Preserve advisory model: the agent recommends; humans decide.

## Behavioral Guardrails

1. Recommendation decision must always be one of: approve, deny, escalate.
2. Recommendation rationale must be non-empty for every output.
3. Tool errors must be surfaced and force safe escalation behavior.
4. Decision precedence must remain deterministic: escalate, then deny, then approve.

## Quality Guardrails

1. All public functions must include type hints.
2. Tool functions must include docstrings describing behavior and return shape.
3. Tests must cover each tool primary path and key edge case.
4. Do not remove failing tests to achieve a pass.

## Traceability Guardrails

1. Map code and spec changes to applicable user stories.
2. Use story-tagged commits in format [US-XXX] Short description.
3. Record test execution evidence in docs/test-results.xml for review gates.
4. Keep Go or No-Go and peer review artifacts evidence-backed.
