from typing import List, Dict, Union

from graphviz import Digraph
from pydantic import BaseModel

from objects.node import Node
from objects.relationship import Relationship
from resources.prompts.prompts import model_generation_rules

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
            # errors+=node.validate_unique_constraints(csv_columns=csv_columns)

        for rel in self.relationships:
            errors+=rel.validate_properties(csv_columns=csv_columns)
            # errors+=rel.validate_unique_constraints(csv_columns=csv_columns)
        
        errors+=self._validate_relationship_sources_and_targets()
        errors+=self._validate_csv_features_used_only_once()
        
        if len(errors) > 0:
            message = f"""
                    The following data model is invalid and must be fixed.
                    Properties must be from the provided Column Options. 
                    Data Model:
                    {self.model_dump()}
                    Errors:
                    {str(errors)}
                    Column Options:
                    {csv_columns}
                    A data model must follow these rules:
                    {model_generation_rules}
                    Consider adding Nodes if they don't exist.
                    Consider moving properties to different nodes.
                    Is there a column option that is semantically similar to an invalid property?
                    Return an explanation of how you will fix each error while following the provided rules.
                    """
            print("validation message: \n", message)
            return {
                "valid": False,
                "message": message,
                "errors": errors
            }
        return {
            "valid": True,
            "message": "",
            "errors": []
        }
    
    def _validate_relationship_sources_and_targets(self) -> List[Union[str, None]]:
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
                
    def _validate_csv_features_used_only_once(self) -> List[Union[str, None]]:
        """
        Validate that each property is used no more than one time in the data model.
        """

        used_features = {}
        errors = []

        for node in self.nodes:
            for prop in node.properties:
                if prop.csv_mapping not in list(used_features.keys()):
                    used_features[prop.csv_mapping] = [node.label]
                else:
                    used_features[prop.csv_mapping].append(node.label)
                    # errors.append(f"The property {prop} is used for {used_features[prop]} in the data model. Each node or relationship must use a different csv column as a property instead.")
        for rel in self.relationships:
            for prop in rel.properties:
                if prop.csv_mapping not in used_features:
                    used_features[prop.csv_mapping] = [rel.type]
                else:
                    used_features[prop.csv_mapping].append(rel.type)
                    # errors.append(f"The property {prop} is used for {used_features[prop]} in the data model. Each node or relationship must use a different csv column as a property instead.")
        for prop, labels_or_types in used_features.items():
            if len(labels_or_types) > 1:
                errors.append(f"The property csv_mapping {prop} is used for {labels_or_types} in the data model. Each of these must use a different csv column as a property csv_mapping instead. Find alternative property csv_mappings from the column options or remove.")

        return errors

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
            result = result + prop.name + f": {prop.csv_mapping}" + (" *unique*" if prop.is_unique else "") + "\n"
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
            result = result + prop.name + f": {prop.csv_mapping}" + (" *unique*" if prop.is_unique else "") + "\n"
            # print(result)

        return result