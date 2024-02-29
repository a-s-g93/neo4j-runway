CREATE CONSTRAINT loan_loannumber IF NOT EXISTS FOR (n:Loan) REQUIRE n.loannumber IS UNIQUE;

CREATE CONSTRAINT borrower_borrowername IF NOT EXISTS FOR (n:Borrower) REQUIRE n.borrowername IS UNIQUE;

LOAD CSV WITH HEADERS FROM 'file:///file_name' as row
CALL {
	WITH row
	MERGE (n:Loan {loannumber: row.LoanNumber})
SET n.jobsreported = row.JobsReported, n.currentapprovalamount = row.CurrentApprovalAmount} IN TRANSACTIONS OF 10000 ROWS;

LOAD CSV WITH HEADERS FROM 'file:///file_name' as row
CALL {
	WITH row
	MERGE (n:Borrower {borrowername: row.BorrowerName})
} IN TRANSACTIONS OF 10000 ROWS;

LOAD CSV WITH HEADERS FROM 'file:///file_name' as row
CALL {
	WITH row
	MERGE (n:Business {})
SET n.businesstype = row.BusinessType} IN TRANSACTIONS OF 10000 ROWS;

LOAD CSV WITH HEADERS FROM 'file:///file_name' as row
CALL {
	WITH row
	MERGE (n:State {})
SET n.projectstate = row.ProjectState} IN TRANSACTIONS OF 10000 ROWS;

LOAD CSV WITH HEADERS FROM 'file:///file_name' as row
CALL {
	WITH row
	MERGE (n:Lender {})
SET n.originatinglender = row.OriginatingLender} IN TRANSACTIONS OF 10000 ROWS;

LOAD CSV WITH HEADERS FROM 'file:///file_name' as row
CALL {
	WITH row
	MERGE (n:LoanProceed {})
SET n.health_care_proceed = row.HEALTH_CARE_PROCEED, n.rent_proceed = row.RENT_PROCEED, n.payroll_proceed = row.PAYROLL_PROCEED, n.utilities_proceed = row.UTILITIES_PROCEED, n.debt_interest_proceed = row.DEBT_INTEREST_PROCEED, n.refinance_eidl_proceed = row.REFINANCE_EIDL_PROCEED, n.mortgage_interest_proceed = row.MORTGAGE_INTEREST_PROCEED} IN TRANSACTIONS OF 10000 ROWS;

LOAD CSV WITH HEADERS FROM 'file:///file_name' as row
CALL {
	WITH row
	MATCH (source:Borrower{borrowername: row.BorrowerName})
	MATCH (target:Loan{loannumber: row.LoanNumber})
	MERGE (source)-[:BORROWED]->(target)
} IN TRANSACTIONS OF 10000 ROWS;

LOAD CSV WITH HEADERS FROM 'file:///file_name' as row
CALL {
	WITH row
	MATCH (source:Loan{loannumber: row.LoanNumber})
	MATCH (target:Business{})
	MERGE (source)-[:BELONGS_TO]->(target)
} IN TRANSACTIONS OF 10000 ROWS;

LOAD CSV WITH HEADERS FROM 'file:///file_name' as row
CALL {
	WITH row
	MATCH (source:Loan{loannumber: row.LoanNumber})
	MATCH (target:State{})
	MERGE (source)-[:LOCATED_IN]->(target)
} IN TRANSACTIONS OF 10000 ROWS;

LOAD CSV WITH HEADERS FROM 'file:///file_name' as row
CALL {
	WITH row
	MATCH (source:Loan{loannumber: row.LoanNumber})
	MATCH (target:Lender{})
	MERGE (source)-[:ORIGINATED_BY]->(target)
} IN TRANSACTIONS OF 10000 ROWS;

LOAD CSV WITH HEADERS FROM 'file:///file_name' as row
CALL {
	WITH row
	MATCH (source:Loan{loannumber: row.LoanNumber})
	MATCH (target:LoanProceed{})
	MERGE (source)-[:PROCEED_USED_FOR]->(target)
} IN TRANSACTIONS OF 10000 ROWS;

