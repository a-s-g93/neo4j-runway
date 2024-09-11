import warnings
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, field_validator


class UserInput(BaseModel):
    """
    A container for user provided information about the data.

    Attributes
    ----------
    general_description : str, optional
        A general description of the CSV data.
    data_dictionary : Dict[str, str], optional
        A mapping of the desired columns to their descriptions.
        If multi-file, then each file name should contain it's own sub dictionary.
        The keys of this argument will determine which CSV columns are
        evaluated in discovery and used to generate a data model.
    use_cases : List[str], optional
        A list of use cases that the final data model should be able to answer.
    """

    general_description: str = ""
    data_dictionary: Dict[str, Any] = dict()
    use_cases: Optional[List[str]] = None

    def __init__(
        self,
        data_dictionary: Dict[str, Any] = dict(),
        general_description: str = "",
        use_cases: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        """
        A container for user provided information about the data.

        Parameters
        ----------
        general_description : str, optional
            A general description of the CSV data, by default = ""
        data_dictionary : Dict[str, str], optional
            A mapping of the desired columns to their descriptions.
            If multi-file, then each file name should contain it's own sub dictionary.
            The leaf values of this argument will determine which columns are
            evaluated in discovery and used to generate a data model.
        use_cases : List[str], optional
            A list of use cases that the final data model should be able to answer.
        """

        # keep support for this arg
        if "column_descriptions" in kwargs:
            data_dictionary = kwargs["column_descriptions"]

        super().__init__(
            general_description=general_description,
            data_dictionary=data_dictionary,
            use_cases=use_cases,
        )

    @field_validator("data_dictionary")
    def validate_data_dictionary(cls, v: Dict[str, Any]) -> Dict[str, str]:
        if any(isinstance(x, int) for x in v.values()):
            raise ValueError("int values may not be present in data dictionary.")
        if v == {}:
            warnings.warn("Empty data dictionary is not recommended.")
        return v

    @property
    def is_multifile(self) -> bool:
        """
        Whether the data dictionary covers multiple files.

        Returns
        -------
        bool
        """

        possible_cols = list(self.data_dictionary.values())
        if len(possible_cols) == 0:
            return False
        return isinstance(possible_cols[0], dict)

    @property
    def allowed_columns(self) -> Union[List[str], Dict[str, List[str]]]:
        """
        The allowed columns.

        Returns
        -------
        Union[List[str], Dict[str, List[str]]]
            single file : A list of columns from the DataFrame.
            Multi file  : a dictionary with keys of file names and A list of columns for each file.
        """

        if not self.is_multifile:
            return list(self.data_dictionary.keys())
        else:
            return {k: list(v.keys()) for k, v in self.data_dictionary.items()}

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
    data_dictionary: Optional[Dict[str, Any]] = None,
    use_cases: Optional[List[str]] = None,
) -> UserInput:
    """
    Safely construct a UserInput object from a given dictionary, allowed columns and use cases.
    This may be used for single file inputs. This function is unable to construct a UserInput instance for
    multi-file inputs.

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

    # check if multifile
    def _is_multifile() -> bool:
        if data_dictionary is not None:
            possible_cols = list(data_dictionary.values())
            if len(possible_cols) == 0:
                return False
            return isinstance(possible_cols[0], dict)
        else:
            return False

    is_multifile = _is_multifile()

    # handle general description
    general_description = (
        unsafe_user_input["general_description"]
        if "general_description" in unsafe_user_input
        else ""
    )
    if "general_description" in unsafe_user_input.keys():
        del unsafe_user_input["general_description"]
    elif not data_dictionary:
        warnings.warn(
            "user_input should include key:value pair {general_description: ...} for best results."
        )

    if not is_multifile:
        # find unmatched columns
        # assume remaining keys indicate columns
        # only check if allowed_columns and unsafe_user_input > 0
        if len(allowed_columns) > 0 and len(unsafe_user_input) > 0:
            diff = set(unsafe_user_input.keys()).difference(set(allowed_columns))
            if len(diff) > 0:
                raise ValueError(
                    f"Column(s) {diff} is/are declared in the provided data_dictionary, but is/are not found in the provided allowed_columns arg: {allowed_columns}."
                )

    # handle column descriptions
    if not unsafe_user_input and not data_dictionary:
        warnings.warn("No columns detected in user input. Defaulting to all columns.")

    return UserInput(
        general_description=general_description,
        data_dictionary=data_dictionary
        or unsafe_user_input
        or {k: "" for k in allowed_columns},
        use_cases=use_cases,
    )
