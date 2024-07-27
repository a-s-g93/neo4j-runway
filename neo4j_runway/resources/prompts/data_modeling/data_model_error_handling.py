from typing import Any, Dict, List, Union
from .constants import DATA_MODEL_GENERATION_RULES


def create_retry_data_model_generation_prompt(
    chain_of_thought_response: str,
    errors_to_fix: str,
    model_to_fix: Union["DataModel", str],  # type: ignore
) -> str:
    """
    Generate a prompt to fix the data model using the errors found in previous model
    and the chain of thought response containing ideas on how to fix the errors.
    """

    return f"""
Fix these errors in the data model by following the recommendations below and following the rules.
Do not return the same model!
{chain_of_thought_response}

Errors:
{errors_to_fix}

Data Model:
{model_to_fix}

Rules that must be followed:
{DATA_MODEL_GENERATION_RULES}
"""


def create_retry_initial_data_model_prep_generation_prompt(invalid_options: Dict[str, Any], errors: List[str]) -> str:  # type: ignore
    """
    Generate a retry prompt for the brainstorming stage of creating an initial data model.

    Parameters
    ----------
    invalid_options : DataModelEntityPool
        The initially returned suggestions that are invalid.
    errors : List[str]
        List of errors present in the suggestions.

    Returns
    -------
    str
        the retry prompt.
    """
    return f"""Fix these errors in the initial data model suggestions below.
Errors:
{errors}

Initial Data Model Suggestions:
{invalid_options}
"""


def create_data_model_errors_cot_prompt(
    data_model_as_dictionary: Dict[str, Any],
    errors: List[str],
    allowed_columns: List[str],
) -> str:
    """
    Generate a prompt to be sent to the LLM to perform a chain of thought response.
    Prmopts the LLM to provide recommendations to solve the given problems.
    No data model should be returned.

    Returns
    -------
    str
        The prompt.
    """

    return f"""
The following data model is invalid and must be fixed.
Properties must be from the provided Column Options. 
Data Model:
{data_model_as_dictionary}
Errors:
{errors}
Column Options:
{allowed_columns}
A data model must follow these rules:
{DATA_MODEL_GENERATION_RULES}
Consider adding Nodes if they don't exist.
Consider moving properties to different nodes.
Is there a column option that is semantically similar to an invalid property?
Return an explanation of how you will fix each error while following the provided rules.
"""
