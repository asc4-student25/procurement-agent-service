# vendor-duplication Specification

## Purpose
TBD - created by archiving change add-procurement-intelligence-agent. Update Purpose after archive.
## Requirements
### Requirement: Single-Source Duplication Rule
The vendor duplication check SHALL enforce POL-001 threshold and category conflict logic.

#### Scenario: Threshold not exceeded
- GIVEN amount less than or equal to 25000.00
- WHEN duplication check is executed
- THEN violation is false

#### Scenario: Active category conflict above threshold
- GIVEN amount greater than 25000.00 and one or more different active vendors in same category
- WHEN duplication check is executed
- THEN violation is true and conflicting vendor details are returned

#### Scenario: No active category conflict above threshold
- GIVEN amount greater than 25000.00 and no different active vendor in same category
- WHEN duplication check is executed
- THEN violation is false

### Requirement: Duplication Response Contract
The duplication check SHALL return violation, vendor_id, category, amount,
conflicting_vendor_ids, conflicting_vendor_names, and reason.

#### Scenario: Standard response keys are present
- GIVEN any duplication check execution path
- WHEN response is returned
- THEN all standard duplication response keys are present

#### Scenario: Violation reason includes policy context
- GIVEN a violation is detected
- WHEN response is returned
- THEN reason references POL-001 and the threshold context

### Requirement: Duplication Check Error Handling
The duplication check SHALL return explicit error context when vendor data is unavailable.

#### Scenario: Vendor data unavailable
- GIVEN vendor data cannot be loaded
- WHEN duplication check is executed
- THEN response includes error and remains safe for escalation behavior

