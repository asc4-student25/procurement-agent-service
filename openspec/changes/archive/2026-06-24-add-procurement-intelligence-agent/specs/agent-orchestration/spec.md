## ADDED Requirements

### Requirement: Full Check Execution
The agent SHALL execute budget, vendor duplication, policy compliance, and risk assessment checks for every request.

#### Scenario: All checks run per request
- GIVEN any valid purchase request
- WHEN the agent evaluates the request
- THEN all four checks are called before final decision synthesis

#### Scenario: No short-circuit behavior
- GIVEN the first executed check returns a blocking finding
- WHEN evaluation continues
- THEN remaining checks still execute and contribute to rationale

### Requirement: Deterministic Decision Precedence
The agent SHALL apply final decision precedence in this order: escalate, then deny, then approve.

#### Scenario: Escalate precedence over deny
- GIVEN findings include both a deny condition and an escalate condition
- WHEN final decision is selected
- THEN decision is escalate

#### Scenario: Deny precedence over approve
- GIVEN findings include one or more deny conditions and no escalate condition
- WHEN final decision is selected
- THEN decision is deny

#### Scenario: Approval path
- GIVEN no deny or escalate conditions across all checks
- WHEN final decision is selected
- THEN decision is approve

### Requirement: Error-Aware Safe Fallback
The agent SHALL escalate when any tool response includes error context.

#### Scenario: Tool failure triggers escalation
- GIVEN one or more checks return an error field
- WHEN final decision is selected
- THEN decision is escalate and rationale includes error context

### Requirement: Structured Recommendation Output
The agent SHALL return output conforming to recommendation schema with non-empty rationale.

#### Scenario: Output contract compliance
- GIVEN any evaluated request
- WHEN recommendation is returned
- THEN decision is one of approve deny escalate and rationale is non-empty

### Requirement: Rationale Traceability Quality
The recommendation rationale SHALL reference concrete findings from checks or policies.

#### Scenario: Deny rationale references a driver
- GIVEN final decision is deny
- WHEN rationale is reviewed
- THEN rationale names at least one concrete driver such as policy id, budget overage, or duplication finding

#### Scenario: Escalate rationale references a driver
- GIVEN final decision is escalate
- WHEN rationale is reviewed
- THEN rationale names escalation driver such as policy escalation, critical risk, or tool error

### Requirement: Decision Reachability on Sample Data
The sample request set SHALL include at least one path to approve, deny, and escalate outcomes.

#### Scenario: All decision classes are reachable
- GIVEN sample requests are evaluated end-to-end
- WHEN outcome set is collected
- THEN at least one approve, one deny, and one escalate decision exist
