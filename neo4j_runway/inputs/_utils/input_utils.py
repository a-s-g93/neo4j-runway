from typing import Any, Dict, List
import warnings

from ..user_input import UserInput


def user_input_safe_construct(
    unsafe_user_input: Dict[str, Any], allowed_columns: List[str] = list()
) -> UserInput:
    """
    Safely construct a UserInput object from a given dictionary.

    Parameters
    ----------
    unsafe_user_input : Dict[str, Any]
        A dictionary containing general_description and column keys.
    allowed_columns : List[str], optional
        A list of allowed columns for the graph data model to use, by default list()

    Returns
    -------
    UserInput
        Contains input data in UserInput format.
    """

    # handle general description
    general_description = (
        unsafe_user_input["general_description"]
        if "general_description" in unsafe_user_input
        else ""
    )
    if "general_description" in unsafe_user_input.keys():
        del unsafe_user_input["general_description"]
    else:
        warnings.warn(
            "user_input should include key:value pair {general_description: ...} for best results."
        )

    # handle column descriptions
    if not unsafe_user_input:
        warnings.warn("No columns detected in user input. Defaulting to all columns.")

    return UserInput(
        general_description=general_description,
        column_descriptions=unsafe_user_input or {k: "" for k in allowed_columns},
    )
