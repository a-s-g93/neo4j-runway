CREATE CONSTRAINT loan_loannumber IF NOT EXISTS FOR (n:Loan) REQUIRE n.loannumber IS UNIQUE;
CREATE CONSTRAINT borrower_borrowername IF NOT EXISTS FOR (n:Borrower) REQUIRE n.borrowername IS UNIQUE;
