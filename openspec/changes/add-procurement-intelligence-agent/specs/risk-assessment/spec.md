## ADDED Requirements

### Requirement: Vendor Risk Classification
The risk assessment check SHALL classify vendor risk level using compliance and contract state.

#### Scenario: Compliance flag yields critical risk
- GIVEN a vendor with active compliance flag
- WHEN risk assessment is executed
- THEN risk level is critical

#### Scenario: Expired contract yields high risk
- GIVEN a vendor with expired contract status
- WHEN risk assessment is executed
- THEN risk level is high

#### Scenario: No contract yields medium risk
- GIVEN a vendor with contract status set to none
- WHEN risk assessment is executed
- THEN risk level is medium

#### Scenario: Active clean contract yields low risk
- GIVEN a vendor with active contract and no compliance flag
- WHEN risk assessment is executed
- THEN risk level is low

### Requirement: Risk Response Contract
The risk assessment check SHALL return vendor_id, vendor_name, compliance_flag,
compliance_notes, contract_status, risk_level, and risk_summary.

#### Scenario: Risk level values are constrained
- GIVEN any successful risk assessment response
- WHEN risk_level is inspected
- THEN risk_level is one of low, medium, high, or critical

#### Scenario: Risk summary is always present
- GIVEN any risk assessment response path
- WHEN response is returned
- THEN risk_summary is a non-empty descriptive string

### Requirement: Risk Check Error Handling
The risk assessment check SHALL return explicit error context for unknown vendors and unavailable data.

#### Scenario: Unknown vendor
- GIVEN a vendor id not found in vendor dataset
- WHEN risk assessment is executed
- THEN response includes error and remains structured

#### Scenario: Vendor data unavailable
- GIVEN vendor data cannot be loaded
- WHEN risk assessment is executed
- THEN response includes error and remains safe for escalation behavior
