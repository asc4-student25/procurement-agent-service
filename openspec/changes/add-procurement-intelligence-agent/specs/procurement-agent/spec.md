# procurement-agent Specification

## Purpose
Define the normative behavior for the procurement recommendation agent in `agent.py`,
including typed contracts, mandatory tool usage, deterministic decision synthesis,
error-aware fallback behavior, and system prompt constraints for Pydantic AI execution.

## Requirements
### Requirement: Typed Input and Output Contract
The procurement agent SHALL accept `PurchaseRequest` as input and SHALL return
`ProcurementRecommendation` as output, as defined in `models.py`.

#### Scenario: Input model usage
- GIVEN a request evaluation is initiated
- WHEN the agent receives request data
- THEN the request is interpreted as `PurchaseRequest`

#### Scenario: Output model usage
- GIVEN evaluation has completed
- WHEN the agent emits a recommendation
- THEN the output is `ProcurementRecommendation`

#### Scenario: Decision and rationale contract
- GIVEN any completed evaluation
- WHEN output is validated
- THEN `decision` is one of `approve`, `deny`, or `escalate`
- AND `rationale` is non-empty

### Requirement: Mandatory Four-Tool Execution
The procurement agent SHALL execute all four procurement checks for every request.

#### Scenario: Tool set is fixed
- GIVEN the agent is configured
- WHEN tool registration is inspected
- THEN the registered tools are exactly:
- AND `check_budget`
- AND `check_vendor_duplication`
- AND `check_policy_compliance`
- AND `assess_risk`

#### Scenario: All tools execute per request
- GIVEN any valid `PurchaseRequest`
- WHEN the agent evaluates the request
- THEN all four tools are called prior to final decision synthesis

#### Scenario: No short-circuit on blocking findings
- GIVEN an early tool returns a deny or escalate condition
- WHEN evaluation continues
- THEN remaining tools still execute
- AND their findings are available to rationale synthesis

### Requirement: Deterministic Decision Priority
The procurement agent SHALL apply decision precedence in this exact order:
`escalate` first, then `deny`, then `approve`.

#### Scenario: Escalate wins over deny
- GIVEN one or more deny drivers and one or more escalate drivers are present
- WHEN final decision is selected
- THEN the recommendation decision is `escalate`

#### Scenario: Deny wins over approve
- GIVEN one or more deny drivers are present and no escalate drivers are present
- WHEN final decision is selected
- THEN the recommendation decision is `deny`

#### Scenario: Approve requires clean checks
- GIVEN no escalate drivers and no deny drivers are present
- WHEN final decision is selected
- THEN the recommendation decision is `approve`

### Requirement: Error-Aware Safe Fallback
The procurement agent SHALL treat tool errors as safety-critical and SHALL escalate.

#### Scenario: Structured error field triggers escalation
- GIVEN any tool response includes non-empty error context
- WHEN final decision is selected
- THEN the recommendation decision is `escalate`

#### Scenario: Unexpected exception is surfaced as escalation context
- GIVEN a tool call raises an unexpected runtime exception
- WHEN evaluation recovers and completes
- THEN the recommendation decision is `escalate`
- AND rationale includes error context indicating which check failed

### Requirement: Prompt-Constrained Agent Behavior
The system prompt SHALL explicitly constrain the model to follow orchestration,
precedence, and rationale traceability rules.

#### Scenario: Prompt requires mandatory checks
- GIVEN the system prompt is defined
- WHEN prompt content is reviewed
- THEN it instructs the agent to run budget, duplication, policy, and risk checks for every request

#### Scenario: Prompt requires precedence policy
- GIVEN the system prompt is defined
- WHEN prompt content is reviewed
- THEN it states precedence `escalate > deny > approve`

#### Scenario: Prompt requires concrete rationale evidence
- GIVEN a recommendation is produced
- WHEN rationale content is reviewed
- THEN rationale references concrete decision drivers such as policy IDs, budget overage,
  risk level, duplication findings, or tool error context

### Requirement: Pydantic AI Structured Output Configuration
The Pydantic AI agent definition SHALL enforce structured output using
`output_type=ProcurementRecommendation`.

#### Scenario: Structured output contract is configured
- GIVEN the agent instance is created
- WHEN construction parameters are inspected
- THEN `output_type` is set to `ProcurementRecommendation`
- AND recommendation responses conform to the schema contract