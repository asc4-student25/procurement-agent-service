# models Specification

## Purpose
TBD - created by archiving change add-procurement-intelligence-agent. Update Purpose after archive.
## Requirements
### Requirement: Purchase Request Input Contract
The system SHALL define a typed Purchase Request model for procurement evaluation.

#### Scenario: Valid request is accepted
- GIVEN a request with positive quantity, unit_price, and total_amount
- WHEN model validation is executed
- THEN validation succeeds and the request is accepted as structured input

#### Scenario: Non-positive numeric fields are rejected
- GIVEN a request where quantity or price or total is less than or equal to zero
- WHEN model validation is executed
- THEN validation fails and the request is rejected

### Requirement: Request Field Completeness
The Purchase Request model SHALL include request_id, requestor, cost_center_id, vendor_name,
vendor_id, category, item_description, quantity, unit_price, and total_amount.

#### Scenario: Missing required field is rejected
- GIVEN a request missing one or more required fields
- WHEN model validation is executed
- THEN validation fails

### Requirement: Procurement Recommendation Output Contract
The system SHALL define a structured recommendation model with strict decision values.

#### Scenario: Valid decision is accepted
- GIVEN a recommendation with decision set to approve or deny or escalate
- WHEN output validation is executed
- THEN validation succeeds

#### Scenario: Invalid decision is rejected
- GIVEN a recommendation with decision outside allowed values
- WHEN output validation is executed
- THEN validation fails

#### Scenario: Empty rationale is rejected
- GIVEN a recommendation with empty or whitespace-only rationale
- WHEN output validation is executed
- THEN validation fails

### Requirement: Structured Agent Output Type
The agent configuration SHALL declare Procurement Recommendation as the structured output type.

#### Scenario: Agent output is schema constrained
- GIVEN the agent is initialized for runtime
- WHEN output configuration is inspected
- THEN output type is bound to the recommendation schema rather than free-form text

