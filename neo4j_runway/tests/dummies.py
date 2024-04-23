import pandas as pd


test_model_valid = {
    "Nodes": [
        {
            "Label": "Loan",
            "Properties": ["LoanNumber", "CurrentApprovalAmount", "JobsReported"],
            "Reasoning": "The 'Loan' node remains the central entity in this dataset. Each loan has a unique 'LoanNumber', and the other properties provide information about the loan's size and impact. These could be important for identifying patterns or anomalies that might indicate fraud.",
        },
        {
            "Label": "Borrower",
            "Properties": ["BorrowerName"],
            "Reasoning": "The 'Borrower' node represents the entity that received the loan. The 'BorrowerName' property can provide insights into who is receiving loans. This could be useful for identifying patterns or anomalies in the types of borrowers that might be associated with fraud.",
        },
        {
            "Label": "Business",
            "Properties": ["BusinessType"],
            "Reasoning": "The 'Business' node represents the type of business that received the loan. The 'BusinessType' property can provide insights into what types of businesses are receiving loans. This could be useful for identifying patterns or anomalies in the types of businesses that might be associated with fraud.",
        },
        {
            "Label": "Lender",
            "Properties": ["OriginatingLender"],
            "Reasoning": "The 'Lender' node represents the entity that originated the loan. The 'OriginatingLender' property can provide insights into which lenders are most active. This could be useful for identifying patterns or anomalies in the lenders that might be associated with fraud.",
        },
        {
            "Label": "Location",
            "Properties": ["ProjectState"],
            "Reasoning": "The 'Location' node represents the geographical location of the project funded by the loan. The 'ProjectState' property can provide insights into where loans are being used. This could be useful for identifying patterns or anomalies in the geographical distribution of loans that might be associated with fraud.",
        },
        {
            "Label": "LoanPurpose",
            "Properties": [
                "UTILITIES_PROCEED",
                "MORTGAGE_INTEREST_PROCEED",
                "RENT_PROCEED",
                "REFINANCE_EIDL_PROCEED",
                "HEALTH_CARE_PROCEED",
                "DEBT_INTEREST_PROCEED",
            ],
            "Reasoning": "The 'LoanPurpose' node represents the purpose of the loan. The properties provide insights into what the loan funds are being used for. This could be useful for identifying patterns or anomalies in the purposes of loans that might be associated with fraud.",
        },
    ],
    "Relationships": [
        {
            "Label": "RECEIVED",
            "Properties": [],
            "From": "Borrower",
            "To": "Loan",
            "Reasoning": "The 'RECEIVED' relationship represents the action of a borrower receiving a loan. This relationship does not have any properties of its own, but it helps to connect the 'Borrower' and 'Loan' nodes and could be useful for identifying patterns or anomalies in the borrowers that might be associated with fraud.",
        },
        {
            "Label": "OPERATES",
            "Properties": [],
            "From": "Borrower",
            "To": "Business",
            "Reasoning": "The 'OPERATES' relationship represents the connection between a borrower and the type of business they operate. This relationship does not have any properties of its own, but it helps to connect the 'Borrower' and 'Business' nodes and could be useful for identifying patterns or anomalies in the types of businesses that might be associated with fraud.",
        },
        {
            "Label": "ORIGINATED",
            "Properties": [],
            "From": "Lender",
            "To": "Loan",
            "Reasoning": "The 'ORIGINATED' relationship represents the action of a lender originating a loan. This relationship does not have any properties of its own, but it helps to connect the 'Lender' and 'Loan' nodes and could be useful for identifying patterns or anomalies in the lenders that might be associated with fraud.",
        },
        {
            "Label": "LOCATED_IN",
            "Properties": [],
            "From": "Loan",
            "To": "Location",
            "Reasoning": "The 'LOCATED_IN' relationship represents the geographical location of the project funded by the loan. This relationship does not have any properties of its own, but it helps to connect the 'Loan' and 'Location' nodes and could be useful for identifying patterns or anomalies in the geographical distribution of loans that might be associated with fraud.",
        },
        {
            "Label": "USED_FOR",
            "Properties": [],
            "From": "Loan",
            "To": "LoanPurpose",
            "Reasoning": "The 'USED_FOR' relationship represents the purpose of the loan. This relationship does not have any properties of its own, but it helps to connect the 'Loan' and 'LoanPurpose' nodes and could be useful for identifying patterns or anomalies in the purposes of loans that might be associated with fraud.",
        },
    ],
}

test_model_invalid = {
    "Nodes": [
        {
            "Label": "Loan",
            "Properties": ["LoanNumber", "CurrentApprovalAmount", "fakeProp"],
            "Reasoning": "The 'Loan' node remains the central entity in this dataset. Each loan has a unique 'LoanNumber', and the other properties provide information about the loan's size and impact. These could be important for identifying patterns or anomalies that might indicate fraud.",
        },
        {
            "Label": "Borrower",
            "Properties": ["BorrowerName"],
            "Reasoning": "The 'Borrower' node represents the entity that received the loan. The 'BorrowerName' property can provide insights into who is receiving loans. This could be useful for identifying patterns or anomalies in the types of borrowers that might be associated with fraud.",
        },
        {
            "Label": "Business",
            "Properties": ["BusinessType"],
            "Reasoning": "The 'Business' node represents the type of business that received the loan. The 'BusinessType' property can provide insights into what types of businesses are receiving loans. This could be useful for identifying patterns or anomalies in the types of businesses that might be associated with fraud.",
        },
        {
            "Label": "Lender",
            "Properties": ["OriginatingLender"],
            "Reasoning": "The 'Lender' node represents the entity that originated the loan. The 'OriginatingLender' property can provide insights into which lenders are most active. This could be useful for identifying patterns or anomalies in the lenders that might be associated with fraud.",
        },
        {
            "Label": "Location",
            "Properties": ["ProjectState"],
            "Reasoning": "The 'Location' node represents the geographical location of the project funded by the loan. The 'ProjectState' property can provide insights into where loans are being used. This could be useful for identifying patterns or anomalies in the geographical distribution of loans that might be associated with fraud.",
        },
        {
            "Label": "LoanPurpose",
            "Properties": [
                "UTILITIES_PROCEED",
                "MORTGAGE_INTEREST_PROCEED",
                "RENT_PROCEED",
                "REFINANCE_EIDL_PROCEED",
                "HEALTH_CARE_PROCEED",
                "DEBT_INTEREST_PROCEED",
            ],
            "Reasoning": "The 'LoanPurpose' node represents the purpose of the loan. The properties provide insights into what the loan funds are being used for. This could be useful for identifying patterns or anomalies in the purposes of loans that might be associated with fraud.",
        },
    ],
    "Relationships": [
        {
            "Label": "RECEIVED",
            "Properties": [],
            "From": "Borrower",
            "To": "Loan",
            "Reasoning": "The 'RECEIVED' relationship represents the action of a borrower receiving a loan. This relationship does not have any properties of its own, but it helps to connect the 'Borrower' and 'Loan' nodes and could be useful for identifying patterns or anomalies in the borrowers that might be associated with fraud.",
        },
        {
            "Label": "OPERATES",
            "Properties": [],
            "From": "Borrower",
            "To": "Business",
            "Reasoning": "The 'OPERATES' relationship represents the connection between a borrower and the type of business they operate. This relationship does not have any properties of its own, but it helps to connect the 'Borrower' and 'Business' nodes and could be useful for identifying patterns or anomalies in the types of businesses that might be associated with fraud.",
        },
        {
            "Label": "ORIGINATED",
            "Properties": [],
            "From": "Lender",
            "To": "Loan",
            "Reasoning": "The 'ORIGINATED' relationship represents the action of a lender originating a loan. This relationship does not have any properties of its own, but it helps to connect the 'Lender' and 'Loan' nodes and could be useful for identifying patterns or anomalies in the lenders that might be associated with fraud.",
        },
        {
            "Label": "LOCATED_IN",
            "Properties": [],
            "From": "Loan",
            "To": "Location",
            "Reasoning": "The 'LOCATED_IN' relationship represents the geographical location of the project funded by the loan. This relationship does not have any properties of its own, but it helps to connect the 'Loan' and 'Location' nodes and could be useful for identifying patterns or anomalies in the geographical distribution of loans that might be associated with fraud.",
        },
        {
            "Label": "USED_FOR",
            "Properties": [],
            "From": "Loan",
            "To": "LoanPurpose",
            "Reasoning": "The 'USED_FOR' relationship represents the purpose of the loan. This relationship does not have any properties of its own, but it helps to connect the 'Loan' and 'LoanPurpose' nodes and could be useful for identifying patterns or anomalies in the purposes of loans that might be associated with fraud.",
        },
    ],
}

test_columns = [
    "BorrowerName",
    "BusinessType",
    "LoanNumber",
    "CurrentApprovalAmount",
    "JobsReported",
    "ProjectState",
    "OriginatingLender",
    "UTILITIES_PROCEED",
    "PAYROLL_PROCEED",
    "MORTGAGE_INTEREST_PROCEED",
    "RENT_PROCEED",
    "REFINANCE_EIDL_PROCEED",
    "HEALTH_CARE_PROCEED",
    "DEBT_INTEREST_PROCEED",
]

test_user_data = {
    "General Description": "The data in my .csv file contains information about financial loans made to businesses.",
    "BorrowerName": "BorrowerName contains the name of the Business that applied for the loan.",
    "BusinessType": "BusinessType contains the type of business (i.e., Corp, Partnership, LLC, etc.)",
    "LoanNumber": "LoanNumber contains the unique identifier for the loan.",
    "CurrentApprovalAmount": "CurrentApprovalAmount contains the financial amount of the loan.",
    "JobsReported": "JobsReported contains the number of jobs the loan supports.",
    "ProjectState": "ProjectState contains the state where the funds will be used.",
    "OriginatingLender": "OriginatingLender contains the lender that originated the loan.",
    "UTILITIES_PROCEED": "UTILITIES_PROCEED contains the amount of the loan the borrower said they will use to pay utilities.",
    "PAYROLL_PROCEED": "PAYROLL_PROCEED contains the amount of the loan the borrower said they will use for payroll.",
    "MORTGAGE_INTEREST_PROCEED": "MORTGAGE_INTEREST_PROCEED contains the amount of the loan the borrower said they will use to pay mortgage interest.",
    "RENT_PROCEED": "RENT_PROCEED contains the amount of the loan the borrower said they will use to pay rent.",
    "REFINANCE_EIDL_PROCEED": "REFINANCE_EIDL_PROCEED contains the amount of the loan the borrower said they will use to refinance an existing loan.",
    "HEALTH_CARE_PROCEED": "HEALTH_CARE_PROCEED contains the amount of the loan the borrower said they will use to pay employee health care.",
    "DEBT_INTEREST_PROCEED": "DEBT_INTEREST_PROCEED contains the amount of the loan the borrower said they will use to pay debt interest.",
}

test_data = pd.read_csv("data/csv/ppp_loan_data.csv")[:10]
