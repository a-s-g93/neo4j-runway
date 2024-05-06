from typing import Dict
from pydantic import BaseModel, Field, field_validator


class UserInput(BaseModel):

    general_description: str = Field(
        default="", description="A general description of the CSV data."
    )
    column_descriptions: Dict[str, str] = Field(
        description="A mapping of the desired csv columns to their descriptions."
    )

    @field_validator("column_descriptions")
    def validate_column_description(cls, v) -> Dict[str, str]:
        if v == {}:
            raise ValueError("Empty column_descriptions dictionary not allowed.")
        return v

    @property
    def formatted_dict(self) -> Dict[str, str]:
        """
        Dictionary representation of the user input to be used in Discovery.
        """

        res = {k: v for k, v in self.column_descriptions.items()}
        res["general_description"] = self.general_description

        return res
