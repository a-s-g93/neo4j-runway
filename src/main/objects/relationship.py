from typing import List, Dict, Union, Any

from pydantic import BaseModel


class Relationship(BaseModel):
    """
    Relationship representation.
    """

    type: str
    properties: List[Union[str, None]]
    unique_constraints: List[Union[str, None]]
    source: str
    target: str

    # def __init__(self, *a, **kw) -> None:
    #     super().__init__(*a, **kw)

    @property
    def dict(self) -> Dict[str, Union[List[str], str]]:
        pass

    @classmethod
    def validate_properties(self, csv_columns: List[str]):
        for prop in self.properties:
            if prop not in csv_columns:
                raise ValueError(f"relationship {self.type} property {prop} does not exist in csv columns.")
    
    @classmethod
    def validate_unique_constraints(self, csv_columns: List[str]):
        for prop in self.unique_constraints:
            if prop not in csv_columns:
                raise ValueError(f"relationship {self.type} unique constraint {prop} does not exist in csv columns.")