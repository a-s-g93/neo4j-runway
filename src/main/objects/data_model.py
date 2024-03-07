from typing import List, Dict, Union

from graphviz import Digraph
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
                    Fix the errors in following data model and return a corrected version. Do not return the same data model.
                    Data Model:
                    {self.dict}
                    Errors:
                    {str(errors)}
                    Column Options:
                    {csv_columns}
                    """
            print("retry message: \n", message)
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
                errors.append(f"The relationship {rel.type} has the source {rel.source} which does not exist in generated Node labels.")
            if rel.target not in self.node_labels:
                errors.append(f"The relationship {rel.type} has the target {rel.target} which does not exist in generated Node labels.")
        return errors
                
    def map_columns_to_values(self, column_mapping: Dict[str, str]) -> None:
        """
        Apply a column mapping to the node labels, relationship types and all properties.
        """

        pass

    def visualize(self) -> Digraph:
        """
        Visualize the data model.
        """

        dot = Digraph(comment="Data Model")

        for node in self.nodes:
            dot.node(name=node.label, label=self._generate_node_text(node=node))
        
        for rel in self.relationships:
            dot.edge(tail_name=rel.source, head_name=rel.target, label=self._generate_relationship_text(relationship=rel))
        
        return dot
    
    @staticmethod
    def _generate_node_text(node: Node) -> str:
        """
        Generate the label, property and unique constraints displayed on a node.
        """

        result = node.label
        # print(result)
        if len(node.properties) > 0:
            result+="\n\nproperties:\n"
            # print(result)
        for prop in node.properties:
            result = result + prop + (" *unique*" if prop in node.unique_constraints else "") + "\n"
            # print(result)

        return result
    
    @staticmethod
    def _generate_relationship_text(relationship: Relationship) -> str:
        """
        Generate the label, property and unique constraints displayed on a relationship.
        """

        result = relationship.type
        # print(result)
        if len(relationship.properties) > 0:
            result+="\n\nproperties:\n"
            # print(result)
        for prop in relationship.properties:
            result = result + prop + (" *unique*" if prop in relationship.unique_constraints else "") + "\n"
            # print(result)

        return result