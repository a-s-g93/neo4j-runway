from typing import List, Dict, Union

from pydantic import BaseModel

from objects.node import Node
from objects.relationship import Relationship


class DataModel(BaseModel):
    """
    Graph Data Model representation.
    """

    nodes: List[Node]
    relationships: List[Relationship]

    def __init__(
        self,
        nodes: List[Node],
        relationships: List[Relationship],
        # csv_columns: List[str],
    ) -> None:
        super().__init__(nodes=nodes, relationships=relationships)


    @property
    def dict(self) -> Dict[str, Union[List[str], str]]:
        return {
            "nodes": [n.__dict__ for n in self.nodes],
            "relationships": [r.__dict__ for r in self.relationships],
        }

    def validate_model(self, csv_columns: List[str]) -> None:
        """
        Validate the model.
        """

        errors = []
        for node in self.nodes:
            errors+=node.validate_properties(csv_columns=csv_columns)
            errors+=node.validate_unique_constraints(csv_columns=csv_columns)

        for rel in self.relationships:
            errors+=rel.validate_properties(csv_columns=csv_columns)
            errors+=rel.validate_unique_constraints(csv_columns=csv_columns)
        # if len(errors) > 0:
        #     print(errors)
            # raise ValueError(str(errors))
        if len(errors) > 0:
            message = f"""
                    Fix the errors in following data model.
                    Data Model:
                    {self.dict}
                    Errors:
                    {errors}
                    """
            return {
                "valid": False,
                "message": str(errors)
            }
        return {
            "valid": True,
            "message": ""
        }
        
    def map_columns_to_values(self, column_mapping: Dict[str, str]) -> None:
        """
        Apply a column mapping to the node labels, relationship types and all properties.
        """

        pass
