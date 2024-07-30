from typing import Any, Dict, List, Optional
import warnings
from pydantic import BaseModel, field_validator


class UserInput(BaseModel):
    """
    A container for user provided information about the data.
    """

    general_description: str = ""
    column_descriptions: Dict[str, str]
    use_cases: Optional[List[str]] = None

    def __init__(
        self,
        column_descriptions: Dict[str, str],
        general_description: str = "",
        use_cases: List[str] = None,
    ) -> None:
        """
        A container for user provided information about the data.

        Attributes
        ----------
        general_description : str, optional
            A general description of the CSV data, by default = ""
        column_descriptions : Dict[str, str]
            A mapping of the desired CSV columns to their descriptions.
            The keys of this argument will determine which CSV columns are
            evaluated in discovery and used to generate a data model.
        use_cases : List[str], optional
            A list of use cases that the final data model should be able to answer.
        """
        super().__init__(
            general_description=general_description,
            column_descriptions=column_descriptions,
            use_cases=use_cases,
        )

    @field_validator("column_descriptions")
    def validate_column_description(cls, v) -> Dict[str, str]:
        if v == {}:
            warnings.warn("Empty column_descriptions dictionary is not recommended.")
        return v

    @property
    def allowed_columns(self) -> List[str]:
        """
        The allowed columns.

        Returns
        -------
        List[str]
            A list of columns from the DataFrame.
        """

        return list(self.column_descriptions.keys())

    @property
    def pretty_use_cases(self) -> str:
        """
        Format the use cases in a more readable format.

        Returns
        -------
        str
            The formatted use cases as a String.
        """

        if self.use_cases is None:
            return ""

        res = ""
        for uc in self.use_cases:
            res += "* " + uc + "\n"
        return res


def user_input_safe_construct(
    unsafe_user_input: Dict[str, Any],
    allowed_columns: List[str] = list(),
    use_cases: Optional[List[str]] = None,
) -> UserInput:
    """
    Safely construct a UserInput object from a given dictionary, allowed columns and use cases.

    Parameters
    ----------
    unsafe_user_input : Dict[str, Any]
        A dictionary containing general_description and column keys.
    allowed_columns : List[str], optional
        A list of allowed columns for the graph data model to use, by default list()
    use_cases : List[str]
        A list of use cases that the final data model should be able to answer.

    Raises
    ------
    ValueError
        If a column descriptions key is not found in the provided allowed_columns arg.

    Warns
    -----
    If general_description is not included in unsafe_user_input arg.
    If no column keys are provided.

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
        use_cases=use_cases,
    )
