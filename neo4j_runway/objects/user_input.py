from typing import Dict
import warnings
from pydantic import BaseModel, Field, field_validator


class UserInput(BaseModel):
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

    general_description: str = Field(
        default="", description="A general description of the CSV data."
    )
    column_descriptions: Dict[str, str] = Field(
        description="A mapping of the desired csv columns to their descriptions."
    )

    @field_validator("column_descriptions")
    def validate_column_description(cls, v) -> Dict[str, str]:
        if v == {}:
            warnings.warn("Empty column_descriptions dictionary is not recommended.")
        return v

    @property
    def formatted_dict(self) -> Dict[str, str]:
        """
        Dictionary representation of the user input to be used in Discovery.
        """

        res = {k: v for k, v in self.column_descriptions.items()}
        res["general_description"] = self.general_description

        return res
