"""
This file contains the DataModel class which is the standard representation of a graph data model in Neo4j Runway.
"""

from ast import literal_eval
import json
from typing import Any, List, Dict, Optional, Union

from graphviz import Digraph
from pydantic import BaseModel
import yaml

from ..arrows.data_model import ArrowsNode, ArrowsRelationship, ArrowsDataModel
from .node import Node
from .relationship import Relationship
from ...resources.prompts.data_modeling import create_data_model_errors_cot_prompt
from ..solutions_workbench import (
    SolutionsWorkbenchDataModel,
    SolutionsWorkbenchNode,
    SolutionsWorkbenchRelationship,
)
from ...utils.naming_conventions import (
    fix_node_label,
    fix_property,
    fix_relationship_type,
)


class DataModel(BaseModel):
    """
    The standard Graph Data Model representation in Neo4j Runway.
    """

    nodes: List[Node]
    relationships: List[Relationship]
    metadata: Optional[Dict[str, Any]] = None

    def __init__(
        self,
        nodes: List[Node],
        relationships: List[Relationship],
        metadata: Optional[Dict[str, Any]] = None,
        use_neo4j_naming_conventions: bool = True,
    ) -> None:
        """
        The standard Graph Data Model representation in Neo4j Runway.

        Attributes
        ----------
        nodes : List[Node]
            A list of the nodes in the data model.
        relationships : List[Relationship]
            A list of the relationships in the data model.
        metadata: Optional[Dict[str, Any]]
            Metadata from an import source such as Solutions Workbench, by default None
        use_neo4j_naming_conventions : bool, optional
            Whether to convert labels, relationships and properties to Neo4j naming conventions, by default True
        """
        super().__init__(
            nodes=nodes,
            relationships=relationships,
            metadata=metadata,
            use_neo4j_naming_conventions=True,
        )

        # default apply Neo4j naming conventions.
        if use_neo4j_naming_conventions:
            self.apply_neo4j_naming_conventions()

    @property
    def node_labels(self) -> List[str]:
        """
        Returns a list of node labels.

        Returns
        -------
        List[str]
            A list of node labels.
        """

        return [n.label for n in self.nodes]

    @property
    def relationship_types(self) -> List[str]:
        """
        Returns a list of relationship types.

        Returns
        -------
        List[str]
            A list of relationship types.
        """

        return [r.type for r in self.relationships]

    @property
    def node_dict(self) -> Dict[str, Node]:
        """
        Returns a dictionary of node label to Node.

        Returns
        -------
        Dict[str, Node]
            A dictionary with node label keys and Node values.
        """

        return {node.label: node for node in self.nodes}

    @property
    def relationship_dict(self) -> Dict[str, Relationship]:
        """
        Returns a dictionary of relationship type to Relationships.

        Returns
        -------
        Dict[str, Relationship]
            A dictionary with relationship type keys and Relationship values.
        """

        return {r.type: r for r in self.relationships}

    def validate_model(self, csv_columns: List[str]) -> Dict[str, Any]:
        """
        Perform additional validation on the data model.

        Parameters
        ----------
        csv_columns : List[str]
            The CSV columns that are allowed in the data model.

        Returns
        -------
        Dict[str, Any]
            A dictionary containing keys 'valid' indicating whether the data model is valid and 'message' containing a list of errors.
        """
        errors = []
        for node in self.nodes:
            errors += node.validate_properties(csv_columns=csv_columns)

        for rel in self.relationships:
            errors += rel.validate_properties(csv_columns=csv_columns)

        errors += self._validate_relationship_sources_and_targets()
        errors += self._validate_csv_features_used_only_once()

        if len(errors) > 0:
            message = create_data_model_errors_cot_prompt(
                data_model_as_dictionary=self.model_dump(),
                errors=errors,
                allowed_columns=csv_columns,
            )

            print("validation message: \n", message)
            return {"valid": False, "message": message, "errors": errors}
        return {"valid": True, "message": "", "errors": list()}

    def _validate_relationship_sources_and_targets(self) -> List[Union[str, None]]:
        """
        Validate the source and target of a relationship exist in the model nodes.
        """

        errors = list()

        for rel in self.relationships:
            # validate exists
            if rel.source not in self.node_labels:
                errors.append(
                    f"The relationship {rel.type} has the source {rel.source} which does not exist in generated Node labels."
                )
            if rel.target not in self.node_labels:
                errors.append(
                    f"The relationship {rel.type} has the target {rel.target} which does not exist in generated Node labels."
                )

            # validate same node label rels
            if rel.source == rel.target:
                valid_props = [
                    prop
                    for prop in self.node_dict[rel.source].properties
                    if prop.csv_mapping_other is not None
                ]
                if len(valid_props) < 1:
                    errors.append(
                        f"The relationship {rel.type} has source and target of the same node label {rel.source}. This is invalid because node {rel.source} has no property with a declared csv_mapping_other attribute."
                    )

        return errors

    def _validate_csv_features_used_only_once(self) -> List[Union[str, None]]:
        """
        Validate that each property is used no more than one time in the data model.
        """

        used_features: Dict[str, List[str]] = dict()
        errors: List[str] = list()

        for node in self.nodes:
            for prop in node.properties:
                if isinstance(prop.csv_mapping, list):
                    for csv_map in prop.csv_mapping:
                        if csv_map not in list(used_features.keys()):
                            used_features[csv_map] = [node.label]
                        else:
                            used_features[csv_map].append(node.label)
                else:
                    if prop.csv_mapping not in list(used_features.keys()):
                        used_features[prop.csv_mapping] = [node.label]
                    else:
                        used_features[prop.csv_mapping].append(node.label)
        for rel in self.relationships:
            for prop in rel.properties:
                if prop.csv_mapping not in used_features:
                    used_features[prop.csv_mapping] = [rel.type]
                else:
                    used_features[prop.csv_mapping].append(rel.type)
        for prop, labels_or_types in used_features.items():
            if len(labels_or_types) > 1:
                errors.append(
                    f"The property csv_mapping {prop} is used for {labels_or_types} in the data model. Each of these must use a different csv column as a property csv_mapping instead. Find alternative property csv_mappings from the column options or remove."
                )

        return errors

    def visualize(self) -> Digraph:
        """
        Visualize the data model using Graphviz. Requires that Graphviz is installed.

        Returns
        -------
        Digraph
            A visual representation of the data model.
        """

        dot = Digraph(comment="Data Model")

        for node in self.nodes:
            dot.node(name=node.label, label=self._generate_node_text(node=node))

        for rel in self.relationships:
            dot.edge(
                tail_name=rel.source,
                head_name=rel.target,
                label=self._generate_relationship_text(relationship=rel),
            )

        return dot

    @staticmethod
    def _generate_node_text(node: Node) -> str:
        """
        Generate the label, property and unique constraints displayed on a node.
        """

        result = node.label
        if len(node.properties) > 0:
            result += "\n\nproperties:\n"
        for prop in node.properties:
            result = (
                result
                + prop.name
                + f": {prop.csv_mapping}"
                + (" *unique*" if prop.is_unique else "")
                + (" *key*" if prop.part_of_key else "")
                + "\n"
            )

        return result

    @staticmethod
    def _generate_relationship_text(relationship: Relationship) -> str:
        """
        Generate the label, property and unique constraints displayed on a relationship.
        """

        result = relationship.type
        if len(relationship.properties) > 0:
            result += "\n\nproperties:\n"
        for prop in relationship.properties:
            result = (
                result
                + prop.name
                + f": {prop.csv_mapping}"
                + (" *unique*" if prop.is_unique else "")
                + (" *key*" if prop.part_of_key else "")
                + "\n"
            )

        return result

    def apply_neo4j_naming_conventions(self) -> None:
        """
        Apply Neo4j naming conventions to all labels, relationships and properties in the data model.
        This is typically performed within the __init__ method automatically.
        """

        # fix node labels and properties
        for node in self.nodes:
            node.label = fix_node_label(node.label)
            for prop in node.properties:
                prop.name = fix_property(prop.name)

        # fix relationship types and properties
        for rel in self.relationships:
            rel.type = fix_relationship_type(rel.type)
            rel.source = fix_node_label(rel.source)
            rel.target = fix_node_label(rel.target)
            for prop in rel.properties:
                prop.name = fix_property(prop.name)

    def to_json(self, file_path: str = "data-model.json") -> Dict[str, any]:
        """
        Output the data model to a json file.

        Parameters
        ----------
        file_path : str, optional
            The file path to write, by default "data-model.json"

        Returns
        -------
        Dict[str, any]
            A Python dictionary version of the json.
        """

        with open(f"{file_path}", "w") as f:
            f.write(self.model_dump_json())

        return self.model_dump_json()

    def to_yaml(
        self, file_path: str = "data-model.yaml", write_file: bool = True
    ) -> str:
        """
        Output the data model to a yaml file and String.

        Parameters
        ----------
        file_path : str, optional
            The file path to write if write_file = True, by default "data-model.yaml"
        write_file : bool, optional
            Whether to write the file, by default True

        Returns
        -------
        str
            A String representation of the yaml file.
        """

        yaml_string = yaml.dump(self.model_dump(exclude=["metadata"]))

        if write_file:
            with open(f"{file_path}", "w") as f:
                f.write(yaml_string)

        return yaml_string

    def to_arrows(
        self, file_path: str = "data-model.json", write_file: bool = True
    ) -> ArrowsDataModel:
        """
        Output the data model to arrows compatible JSON file.

        Parameters
        ----------
        file_path : str, optional
            The file path to write if write_file = True, by default "data-model.json"
        write_file : bool, optional
            Whether to write the file, by default True

        Returns
        -------
        ArrowsDataModel
            A representation of the data model in arrows.app format.
        """

        NODE_SPACING: int = 200
        y_current = 0
        arrows_nodes = []
        for idx, n in enumerate(self.nodes):
            if (idx + 1) % 5 == 0:
                y_current -= 200
            arrows_nodes.append(
                n.to_arrows(x_position=NODE_SPACING * (idx % 5), y_position=y_current)
            )

        arrows_data_model = ArrowsDataModel(
            nodes=arrows_nodes,
            relationships=[r.to_arrows() for r in self.relationships],
        )
        if write_file:
            with open(f"{file_path}", "w") as f:
                f.write(arrows_data_model.model_dump_json())

        return arrows_data_model

    @classmethod
    def from_arrows(cls, file_path: str) -> "DataModel":
        """
        Construct a DataModel from an arrows data model JSON file.

        Parameters
        ----------
        file_path : str
            The location and name of the arrows.app JSON file to import.

        Returns
        -------
        DataModel
            An instance of a DataModel.
        """

        with open(f"{file_path}", "r") as f:
            content = literal_eval(f.read())
            node_id_to_label_map = {n["id"]: n["labels"][0] for n in content["nodes"]}
            return cls(
                nodes=[
                    Node.from_arrows(
                        ArrowsNode(
                            id=n["id"],
                            position=n["position"],
                            labels=n["labels"],
                            properties=n["properties"],
                            caption=n["caption"],
                            style=n["style"],
                        )
                    )
                    for n in content["nodes"]
                ],
                relationships=[
                    Relationship.from_arrows(
                        ArrowsRelationship(
                            id=r["id"],
                            fromId=r["fromId"],
                            toId=r["toId"],
                            properties=r["properties"],
                            type=r["type"],
                            style=r["style"],
                        ),
                        node_id_to_label_map=node_id_to_label_map,
                    )
                    for r in content["relationships"]
                ],
            )

    def to_solutions_workbench(
        self, file_path: str = "data-model.json", write_file: bool = True
    ) -> SolutionsWorkbenchDataModel:
        """
        Output the data model to Solutions Workbench compatible JSON file.

        Parameters
        ----------
        file_path : str, optional
            The file path to write if write_file = True, by default "data-model.json"
        write_file : bool, optional
            Whether to write the file, by default True

        Returns
        -------
        SolutionsWorkbenchDataModel
            A representation of the data model in Solutions Workbench format.
        """

        X_OFFSET: int = 500
        NODE_SPACING: int = 200
        Y_OFFSET: int = 300
        y_current = 0 + Y_OFFSET
        sw_nodes = dict()
        for idx, n in enumerate(self.nodes):
            if (idx + 1) % 5 == 0:
                y_current -= 200
            sw_nodes[n.label] = n.to_solutions_workbench(
                key=n.label, x=X_OFFSET + (NODE_SPACING * (idx % 5)), y=y_current
            )

        solutions_workbench_data_model = SolutionsWorkbenchDataModel(
            nodeLabels=sw_nodes,
            relationshipTypes={
                r.type + str(i): r.to_solutions_workbench(key=r.type + str(i))
                for i, r in enumerate(self.relationships)
            },
            metadata=self.metadata if self.metadata else dict(),
        )

        if write_file:
            with open(f"{file_path}", "w") as f:
                f.write(solutions_workbench_data_model.model_dump_json())

        return solutions_workbench_data_model

    @classmethod
    def from_solutions_workbench(cls, file_path: str) -> "DataModel":
        """
        Construct a DataModel from a Solutions Workbench data model JSON file.

        Parameters
        ----------
        file_path : str
            The location and name of the Solutions Workbench JSON file to import.

        Returns
        -------
        DataModel
            An instance of a DataModel.
        """

        with open(f"{file_path}", "r") as f:
            content = json.loads(f.read())
            node_id_to_label_map = {
                n["key"]: n["label"]
                for n in content["dataModel"]["nodeLabels"].values()
            }
            return cls(
                nodes=[
                    Node.from_solutions_workbench(SolutionsWorkbenchNode(**n))
                    # print(n, "\n")
                    for n in content["dataModel"]["nodeLabels"].values()
                ],
                relationships=[
                    Relationship.from_solutions_workbench(
                        SolutionsWorkbenchRelationship(**r),
                        node_id_to_label_map=node_id_to_label_map,
                    )
                    for r in content["dataModel"]["relationshipTypes"].values()
                ],
                metadata=content["metadata"],
            )
