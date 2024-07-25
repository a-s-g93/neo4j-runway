from typing import Dict, List
import warnings
from pydantic import BaseModel, Field, field_validator


class UserInput(BaseModel):
    """
    A container for user provided information about the data.
    """

    general_description: str = ""
    column_descriptions: Dict[str, str]

    def __init__(
        self, column_descriptions: Dict[str, str], general_description: str = ""
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
        """
        super().__init__(
            general_description=general_description,
            column_descriptions=column_descriptions,
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