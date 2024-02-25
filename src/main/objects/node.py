from typing import List, Dict, Union, Any

from pydantic import BaseModel


class Node(BaseModel):
    """
    Node representation.
    """

    label: str
    properties: Union[List[str], None] = []
    unique_constraints: Union[List[Union[str, None]], None] = []

    def __init__(self, *a, **kw) -> None:
        super().__init__(*a, **kw)

    @property
    def dict(self) -> Dict[str, Union[List[str], str]]:
        pass

    def validate_properties(self, csv_columns: List[str]) -> List[Union[str, None]]:
        errors = []
        if self.properties is not None:
            for prop in self.properties:
                if prop not in csv_columns:
                    # raise ValueError(
                    errors.append(f"The node {self.label} has the property {prop} which does not exist in csv columns.")
                    # )
        return errors

    def validate_unique_constraints(self, csv_columns: List[str]) -> List[Union[str, None]]:
        errors = []
        if self.unique_constraints is not None:
            for prop in self.unique_constraints:
                if prop not in csv_columns:
                    # raise ValueError(
                    errors.append(f"The node {self.label} has a unique constraint {prop} which does not exist in csv columns.")
                    # )
        return errors
