# policy-compliance Specification

## Purpose
TBD - created by archiving change add-procurement-intelligence-agent. Update Purpose after archive.
## Requirements
### Requirement: Policy Violation Evaluation
The policy compliance check SHALL evaluate requests against procurement policy rules and return structured violations.

#### Scenario: Catering request is denied
- GIVEN a request in catering category
- WHEN policy compliance check is executed
- THEN violations include POL-004 with forced decision deny

#### Scenario: Expired contract vendor is denied
- GIVEN a vendor with expired contract status
- WHEN policy compliance check is executed
- THEN violations include POL-005 with forced decision deny

#### Scenario: Compliance-flagged vendor is escalated
- GIVEN a vendor with active compliance flag
- WHEN policy compliance check is executed
- THEN violations include POL-006 and highest severity is escalate

#### Scenario: Director threshold escalation
- GIVEN a request amount at or above the director approval threshold
- WHEN policy compliance check is executed
- THEN violations include POL-003 with forced decision escalate

#### Scenario: Near-threshold escalation
- GIVEN a request amount within configured near-threshold band below director threshold
- WHEN policy compliance check is executed
- THEN violations include POL-003 with forced decision escalate

#### Scenario: Staffing threshold denial
- GIVEN category is staffing and quantity exceeds 40 and vendor is not under active staffing contract
- WHEN policy compliance check is executed
- THEN violations include staffing policy denial behavior

#### Scenario: Escalate overrides deny in severity summary
- GIVEN violations include both deny and escalate forced decisions
- WHEN highest severity is computed
- THEN highest severity is escalate

#### Scenario: No policy violations
- GIVEN a clean request with no policy trigger
- WHEN policy compliance check is executed
- THEN violations are empty and highest severity is none

### Requirement: Policy Response Contract
The policy compliance check SHALL return violations, violation_count, and highest_severity.

#### Scenario: Highest severity values are constrained
- GIVEN any policy check execution path
- WHEN highest severity is produced
- THEN highest_severity is one of escalate, deny, or none

#### Scenario: Violation entries are structured
- GIVEN one or more violations are produced
- WHEN violations are inspected
- THEN each violation includes policy_id, rule_description, and forced_decision

### Requirement: Policy Check Error Handling
The policy compliance check SHALL return explicit error context when required policy or vendor data is unavailable.

#### Scenario: Policy or vendor data unavailable
- GIVEN policy or vendor data cannot be loaded
- WHEN policy compliance check is executed
- THEN response includes error and remains safe for escalation behavior

