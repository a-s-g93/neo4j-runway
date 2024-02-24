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
    
    @property
    def node_labels(self) -> List[str]:
        """
        Return a list of the node labels.
        """

        return [n.label for n in self.nodes]
    
    @property
    def relationship_types(self) -> List[str]:
        """
        Return a list of the relationship types.
        """

        return [r.type for r in self.relationships]

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
        
        errors+=self.validate_relationship_sources_and_targets()
        
        if len(errors) > 0:
            message = f"""
                    Fix the errors in following data model.
                    Data Model:
                    {self.dict}
                    Errors:
                    {str(errors)}
                    """
            return {
                "valid": False,
                "message": message
            }
        return {
            "valid": True,
            "message": ""
        }
    
    def validate_relationship_sources_and_targets(self) -> List[Union[str, None]]:
        """
        Validate the source and target of a relationship exist in the model nodes.
        """

        errors = []
        for rel in self.relationships:
            if rel.source not in self.node_labels:
                errors.append(f"relationship {rel.type} source {rel.source} does not exist in generated Node labels.")
            if rel.target not in self.node_labels:
                errors.append(f"relationship {rel.type} target {rel.target} does not exist in generated Node labels.")
        return errors
                
    def map_columns_to_values(self, column_mapping: Dict[str, str]) -> None:
        """
        Apply a column mapping to the node labels, relationship types and all properties.
        """

        pass
