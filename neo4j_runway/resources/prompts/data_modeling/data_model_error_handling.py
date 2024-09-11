from typing import Any, Dict, List, Optional

from .formatters import get_rules
from .template import create_data_modeling_prompt


def create_retry_data_model_generation_prompt(
    chain_of_thought_response: str,
    errors_to_fix: List[str],
    model_to_fix: "DataModel",  # type: ignore
    multifile: bool,
    valid_columns: Dict[str, Any],
    data_dictionary: Dict[str, Any],
    use_yaml_data_model: bool = False,
) -> str:
    """
    Generate a prompt to fix the data model using the errors found in previous model
    and the chain of thought response containing ideas on how to fix the errors.
    """

    prefix = "Fix these errors in the data model by following the recommendations below and following the rules. Do not return the same model!"
    rules = get_rules(multifile=multifile, advanced_rules=False)

    return create_data_modeling_prompt(
        prefix=prefix,
        rules=rules,
        corrections=chain_of_thought_response,
        errors=errors_to_fix,
        data_dictionary=data_dictionary,
        multifile=multifile,
        valid_columns=valid_columns,
        data_model=model_to_fix,
        data_model_as_yaml=use_yaml_data_model,
        retry_prompt=True,
    )


def create_retry_initial_data_model_prep_generation_prompt(
    invalid_options: "DataModelEntityPool",  # type: ignore
    errors: List[str],
    data_dictionary: Dict[str, Any],
    multifile: bool,
    valid_columns: Dict[str, Any],
) -> str:
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
    prefix = "Fix these errors in the initial data model suggestions below."

    return create_data_modeling_prompt(
        prefix=prefix,
        errors=errors,
        data_dictionary=data_dictionary,
        multifile=multifile,
        valid_columns=valid_columns,
        entity_pool=invalid_options,
        retry_prompt=True,
        rules="",
    )


def create_data_model_errors_cot_prompt(
    data_model: "DataModel",  # type: ignore
    errors: List[str],
    valid_columns: Dict[str, List[str]],
    multifile: bool,
    data_dictionary: Dict[str, Any],
) -> str:
    """
    Generate a prompt to be sent to the LLM to perform a chain of thought response.
    Prompts the LLM to provide recommendations to solve the given problems.
    No data model should be returned.

    Returns
    -------
    str
        The prompt.
    """
    prefix = """The following data model is invalid and must be fixed.
Properties must be from the provided Column Options."""
    suffix = "Return an explanation of how you will fix each error while following the provided rules."
    rules = get_rules(multifile=multifile, advanced_rules=False)

    return create_data_modeling_prompt(
        prefix=prefix,
        suffix=suffix,
        rules=rules,
        data_dictionary=data_dictionary,
        multifile=multifile,
        data_model=data_model,
        errors=errors,
        valid_columns=valid_columns,
    )


#     return f"""

# Data Model:
# {data_model_as_dictionary}
# Errors:
# {errors}

# {data_dictionary_text}

# Properties must only be derived from these values:
# {valid_columns}

# A data model must follow these rules:
# {rules}


# """


# Column Options:
# {allowed_columns}

# Consider adding Nodes if they don't exist.
# Consider moving properties to different nodes.
# Is there a column option that is semantically similar to an invalid property?
