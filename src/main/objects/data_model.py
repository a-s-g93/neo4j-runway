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
        csv_colums: List[str],
    ) -> None:
        super().__init__(nodes=nodes, relationships=relationships)

        for node in nodes:
            node.validate_properties(csv_columns=csv_colums)
            node.validate_unique_constraints(csv_columns=csv_colums)

        for rel in relationships:
            rel.validate_properties(csv_columns=csv_colums)
            rel.validate_unique_constraints(csv_columns=csv_colums)

    @property
    def dict(self) -> Dict[str, Union[List[str], str]]:
        return {
            "nodes": self.nodes.__dict__,
            "relationships": self.relationships.__dict__,
        }

    def map_columns_to_values(self, column_mapping: Dict[str, str]) -> None:
        """
        Apply a column mapping to the node labels, relationship types and all properties.
        """

        pass
