import warnings
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator

from ..utils.data.data_dictionary.data_dictionary import DataDictionary
from ..utils.data.data_dictionary.utils import (
    load_data_dictionary_from_compact_python_dictionary,
)


class UserInput(BaseModel):
    """
    A container for user provided information about the data.

    Attributes
    ----------
    general_description : str, optional
        A general description of the CSV data.
    data_dictionary :Union[Dict[str, Any], DataDictionary], optional
        A mapping of the desired columns to their descriptions.
        If multi-file, then each file name should contain it's own sub dictionary.
        The keys of this argument will determine which CSV columns are
        evaluated in discovery and used to generate a data model.
    use_cases : List[str], optional
        A list of use cases that the final data model should be able to answer.
    """

    general_description: str = ""
    data_dictionary: DataDictionary
    use_cases: Optional[List[str]] = None

    # def __init__(
    #     self,
    #     data_dictionary: Union[Dict[str, Any], DataDictionary] = dict(),
    #     general_description: str = "",
    #     use_cases: Optional[List[str]] = None,
    #     **kwargs: Any,
    # ) -> None:
    #     """
    #     A container for user provided information about the data.

    #     Parameters
    #     ----------
    #     general_description : str, optional
    #         A general description of the CSV data, by default = ""
    #     data_dictionary : Union[Dict[str, Any], DataDictionary], optional
    #         A mapping of the desired columns to their descriptions.
    #         If multi-file, then each file name should contain it's own sub dictionary.
    #         The leaf values of this argument will determine which columns are
    #         evaluated in discovery and used to generate a data model.
    #     use_cases : List[str], optional
    #         A list of use cases that the final data model should be able to answer.
    #     """

    #     # keep support for this arg
    #     if "column_descriptions" in kwargs:
    #         data_dictionary = kwargs["column_descriptions"]

    #     super().__init__(
    #         general_description=general_description,
    #         data_dictionary=data_dictionary,
    #         use_cases=use_cases,
    #     )

    @field_validator("data_dictionary", mode="before")
    def validate_data_dictionary(
        cls, v: Union[Dict[str, Any], DataDictionary]
    ) -> DataDictionary:
        if not v:
            warnings.warn("Empty data dictionary is not recommended.")
        if isinstance(v, dict):
            try:
                return load_data_dictionary_from_compact_python_dictionary(v)
            except Exception as e:
                raise ValueError(
                    f"Unable to parse provided `data_dictionary` arg into a `DataDictionary` object. Error: {e}"
                )
        assert isinstance(
            v, DataDictionary
        ), "`data_dictionary` arg is not a `DataDictionary` object."

        return v

    @property
    def is_multifile(self) -> bool:
        """
        Whether the data dictionary covers multiple files.

        Returns
        -------
        bool
        """

        return self.data_dictionary.is_multifile

    @property
    def allowed_columns(self) -> Dict[str, List[str]]:
        """
        The allowed columns.

        Returns
        -------
        Dict[str, List[str]]
            A dictionary with keys of file names and a list of columns for each file.
        """

        return self.data_dictionary.table_column_names_dict

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
    data_dictionary: Optional[DataDictionary] = None,
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
            possible_cols = list(data_dictionary.table_schemas[0].column_names)
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
        or load_data_dictionary_from_compact_python_dictionary(unsafe_user_input)
        or load_data_dictionary_from_compact_python_dictionary(
            {k: "" for k in allowed_columns}
        ),
        use_cases=use_cases or unsafe_user_input.get("use_cases"),
    )
