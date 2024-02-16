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

    # def __init__(self, *a, **kw) -> None:
    #     super().__init__(*a, **kw)
    
    @property
    def dict(self) -> Dict[str, Union[List[str], str]]:
        return {"nodes": self.nodes.__dict__,
                "relationships": self.relationships.__dict__}

    def map_columns_to_values(self, column_mapping: Dict[str, str]) -> None:
        """
        Apply a column mapping to the node labels, relationship types and all properties.
        """

        pass