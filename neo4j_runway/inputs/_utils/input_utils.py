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

    Raises
    ------
    ValueError
        If a column descriptions key is not found in the provided allowed_columns arg.

    Warns
    -----
    If general_description is not included in unsafe_user_input arg.

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

    # find unmatched columns
    # assume remaining keys indicate columns
    # only check if allowed_columns and unsafe_user_input > 0
    if len(allowed_columns) > 0 and len(unsafe_user_input) > 0:
        diff = set(unsafe_user_input.keys()).difference(set(allowed_columns))
        if len(diff) > 0:
            raise ValueError(
                f"Column(s) {diff} is/are declared in the provided column descriptions, but is/are not found in the provided allowed_columns arg: {allowed_columns}."
            )

    # handle column descriptions
    if not unsafe_user_input:
        warnings.warn("No columns detected in user input. Defaulting to all columns.")

    return UserInput(
        general_description=general_description,
        column_descriptions=unsafe_user_input or {k: "" for k in allowed_columns},
    )
