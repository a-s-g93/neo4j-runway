from typing import List, Dict, Union, Any

from pydantic import BaseModel, field_validator, ValidationInfo


class Node(BaseModel):
    """
    Node representation.
    """

    label: str
    properties: List[str]
    unique_constraints: Union[List[Union[str, None]], None]

    # def __init__(self, *a, **kw) -> None:
    #     super().__init__(*a, **kw)

    @property
    def dict(self) -> Dict[str, Union[List[str], str]]:
        pass

    @classmethod
    def validate_properties(self, csv_columns: List[str]):
        for prop in self.properties:
            if prop not in csv_columns:
                raise ValueError(f"node {self.label} property {prop} does not exist in csv columns.")
    
    @classmethod
    def validate_unique_constraints(self, csv_columns: List[str]):
        for prop in self.unique_constraints:
            if prop not in csv_columns:
                raise ValueError(f"node {self.label} unique constraint {prop} does not exist in csv columns.")