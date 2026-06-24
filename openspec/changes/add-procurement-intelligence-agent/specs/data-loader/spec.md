## ADDED Requirements

### Requirement: Centralized Data Access
The system SHALL provide a single loader module as the only access path for reference datasets.

#### Scenario: Loader returns known datasets
- GIVEN existing mock data files
- WHEN load functions for budgets, vendors, policies, and requests are called
- THEN each function returns a parsed list of records

#### Scenario: Missing data file surfaces explicit failure
- GIVEN one required data file is missing
- WHEN the related loader function is called
- THEN a file-not-found error is raised or surfaced to callers

### Requirement: Loader API Surface
The loader SHALL expose load_budgets, load_vendors, load_policies, and load_requests functions.

#### Scenario: Loader functions return list-shaped data
- GIVEN any of the four loader functions is called with valid data files present
- WHEN the function returns
- THEN the return type is a list of record objects

### Requirement: Path Resolution Independence
The loader SHALL resolve fixture paths independent of process working directory.

#### Scenario: Loader works from non-root working directory
- GIVEN process working directory is not project root
- WHEN a loader function is called
- THEN the correct fixture file is still located and loaded

### Requirement: Reference Data Assumptions
The specification SHALL define the fixture assumptions used to drive policy and outcome tests.

#### Scenario: Budget fixture contains known budget edge case
- GIVEN budgets fixture is loaded
- WHEN records are inspected
- THEN cost center CC-003 exists with remaining budget 6900 for budget-overage test design

#### Scenario: Vendor fixture contains known compliance and contract edge cases
- GIVEN vendors fixture is loaded
- WHEN records are inspected
- THEN vendor V-006 exists as compliance-flagged and vendor V-010 exists with expired contract status

#### Scenario: Policy fixture contains catering prohibition rule
- GIVEN policies fixture is loaded
- WHEN policy ids are inspected
- THEN POL-004 exists and represents catering prohibition behavior

#### Scenario: Request fixture supports outcome traceability
- GIVEN requests fixture is loaded
- WHEN sample requests are reviewed
- THEN the dataset contains cases supporting approve deny and escalate decision paths

### Requirement: Tools Use Loader Only
Tool modules SHALL consume fixture data through loader functions and not direct file reads.

#### Scenario: Tool data access path is compliant
- GIVEN tool implementations are inspected
- WHEN data access statements are reviewed
- THEN tools import and use loader functions instead of direct JSON file reads
