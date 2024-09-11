"""
This file contains the DataModel class which is the standard representation of a graph data model in Neo4j Runway.
"""

import json
from ast import literal_eval
from typing import Any, Dict, List, Optional

import yaml
from graphviz import Digraph
from pydantic import BaseModel

from ...exceptions import (
    InvalidArrowsDataModelError,
    InvalidSolutionsWorkbenchDataModelError,
)
from ...resources.prompts.data_modeling import create_data_model_errors_cot_prompt
from ...utils.naming_conventions import (
    fix_node_label,
    fix_property,
    fix_relationship_type,
)
from ..arrows import ArrowsDataModel, ArrowsNode, ArrowsRelationship
from ..solutions_workbench import (
    SolutionsWorkbenchDataModel,
    SolutionsWorkbenchNode,
    SolutionsWorkbenchRelationship,
)
from .node import Node
from .relationship import Relationship


class DataModel(BaseModel):
    """
    The standard Graph Data Model representation in Neo4j Runway.

    Attributes
    ----------
    nodes : List[Node]
        A list of the nodes in the data model.
    relationships : List[Relationship]
        A list of the relationships in the data model.
    metadata: Optional[Dict[str, Any]]
        Metadata from an import source such as Solutions Workbench.
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

        Parameters
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

    def validate_model(
        self,
        valid_columns: Dict[str, List[str]],
        data_dictionary: Dict[str, Any],
        allow_duplicate_properties: bool = False,
        enforce_uniqueness: bool = True,
    ) -> Dict[str, Any]:
        """
        Perform additional validation on the data model.

        Parameters
        ----------
        valid_columns : List[str]
            The CSV columns that are allowed in the data model.
        data_dictionary : Dict[str, Any]
            A data dictionary to validate against.
        allow_duplicate_properties : bool, optional
            Whether to allow identical properties to exist on multiple node labels or relationship types, by default False
        enforce_uniqueness : bool, optional
            Whether to error if a node has no unique identifiers (unique or node key).
            Setting this to false may be detrimental during code generation and ingestion. By default True

        Returns
        -------
        Dict[str, Any]
            A dictionary containing keys 'valid' indicating whether the data model is valid and 'message' containing a list of errors.
        """

        errors = list()

        for node in self.nodes:
            errors += node.validate_source_name(valid_columns=valid_columns)
            errors += node.validate_properties(valid_columns=valid_columns)
            if enforce_uniqueness:
                errors += node.enforce_uniqueness()

        for rel in self.relationships:
            errors += rel.validate_source_name(valid_columns=valid_columns)
            errors += rel.validate_properties(valid_columns=valid_columns)

        errors += self._validate_relationship_sources_and_targets(
            valid_columns=valid_columns, data_dictionary=data_dictionary
        )

        if not allow_duplicate_properties:
            errors += self._validate_csv_features_used_only_once()

        if len(errors) > 0:
            message = create_data_model_errors_cot_prompt(
                data_model=self,
                errors=errors,  # type: ignore[arg-type]
                valid_columns=valid_columns,
                multifile=len(valid_columns.keys()) > 1,
                data_dictionary=data_dictionary,
            )

            return {"valid": False, "message": message, "errors": errors}

        return {"valid": True, "message": "", "errors": list()}

    def _validate_relationship_sources_and_targets(
        self, valid_columns: Dict[str, List[str]], data_dictionary: Dict[str, Any]
    ) -> List[str]:
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
                    if prop.alias is not None
                ]
                if len(valid_props) < 1:
                    errors.append(
                        f"The relationship {rel.type} has source and target of the same node label {rel.source}. This is invalid because node {rel.source} has no property with a declared alias attribute."
                    )

            # validate rels that span across files
            # use data dictionary here since aliases shouldn't be used in the data model
            source_node = self.node_dict.get(rel.source)
            target_node = self.node_dict.get(rel.target)

            if source_node is not None and rel.source_name != source_node.source_name:
                for prop in source_node.unique_properties:
                    if prop.alias is None:
                        errors.append(
                            f"The source node {source_node.label} and relationship `{rel.type}` are from different files. The alias of unique property `{prop.name}` on source node `{source_node.label}` must be found in file `{rel.source_name}` and is identified by the attribute `alias`."
                        )
                    elif prop.alias not in data_dictionary[rel.source_name]:
                        errors.append(
                            f"Node `{source_node.label}` Property `{prop.name}` is not found in the file `{rel.source_name}` by the name `{prop.alias}`. Find an alias for unique property `{prop.name}` on source node `{source_node.label}` in file `{rel.source_name}` and identify it on the Property attribute `alias`. Reference the data dictionary for possible alias."
                        )

            if target_node is not None and rel.source_name != target_node.source_name:
                for prop in target_node.unique_properties:
                    if prop.alias is None:
                        errors.append(
                            f"The target node {target_node.label} and relationship `{rel.type}` are from different files. The alias of unique property `{prop.name}` on target node `{target_node.label}` must be found in file `{rel.source_name}` and is identified by the attribute `alias`."
                        )
                    elif prop.alias not in data_dictionary[rel.source_name]:
                        errors.append(
                            f"Node `{target_node.label}` Property `{prop.name}` is not found in the file `{rel.source_name}` by the name `{prop.alias}`. Find an alias for unique property `{prop.name}` on target node `{target_node.label}` in file `{rel.source_name}` and identify it on the Property attribute `alias`. Reference the data dictionary for possible alias."
                        )

        return errors

    def _validate_csv_features_used_only_once(self) -> List[str]:
        """
        Validate that each property is used no more than one time in the data model.
        """

        used_features: Dict[str, Dict[str, List[str]]] = dict()
        # --- used_features example ---
        # file to feature to labels
        # {
        # "a.csv": {"feature_a": ["LabelA", "LabelB"]},
        # "b.csv": {"feature_b": ["LabelA", "LabelB"],
        #           "feature_c": ["LabelD"]},
        # "c.csv": {}
        # }
        # -----------------------------
        errors: List[str] = list()

        for node in self.nodes:
            # init the file dictionary
            if node.source_name not in used_features.keys():
                used_features[node.source_name] = dict()
            for prop in node.properties:
                # if isinstance(prop.column_mapping, list):
                #     for csv_map in prop.column_mapping:
                #         if csv_map not in list(used_features.keys()):
                #             used_features[node.source_name][csv_map] = [node.label]
                #         else:
                #             used_features[csv_map].append(node.label)
                # else:
                if prop.column_mapping not in list(
                    used_features[node.source_name].keys()
                ):
                    used_features[node.source_name][prop.column_mapping] = [node.label]
                else:
                    used_features[node.source_name][prop.column_mapping].append(
                        node.label
                    )

        for rel in self.relationships:
            # init the file dictionary
            if rel.source_name not in used_features.keys():
                used_features[rel.source_name] = dict()
            for prop in rel.properties:
                if prop.column_mapping not in list(
                    used_features[rel.source_name].keys()
                ):
                    used_features[rel.source_name][prop.column_mapping] = [rel.type]
                else:
                    used_features[rel.source_name][prop.column_mapping].append(rel.type)

        for source_name, feature_dict in used_features.items():
            for prop_mapping, labels_or_types in feature_dict.items():
                if len(labels_or_types) > 1:
                    errors.append(
                        f"The Property `column_mapping` {prop_mapping} from file {source_name} is used for {labels_or_types} in the data model. Each of these must use a different column as a Property attribute `column_mapping` instead. Find alternative Property `column_mapping` from the column options in the `source_name` file or remove."
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
                + f": {prop.column_mapping}"
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
                + f": {prop.column_mapping}"
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

    def to_json(self, file_path: str = "data-model.json") -> Dict[str, Any]:
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

        return self.model_dump()

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

        yaml_string = yaml.dump(self.model_dump(exclude={"metadata"}))

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

        Raises
        ------
        InvalidArrowsDataModelError
            If the json file is unable to be parsed.

        Returns
        -------
        DataModel
            An instance of a DataModel.
        """
        try:
            with open(f"{file_path}", "r") as f:
                content = literal_eval(f.read())
                node_id_to_label_map = {
                    n["id"]: n["labels"][0] for n in content["nodes"]
                }
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
        except Exception:
            raise InvalidArrowsDataModelError(
                "Unable to parse the provided arrows.app data model json file."
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

        Raises
        ------
        InvalidSolutionsWorkbenchDataModelError
            If the json file is unable to be parsed.

        Returns
        -------
        DataModel
            An instance of a DataModel.
        """

        try:
            with open(f"{file_path}", "r") as f:
                content = json.loads(f.read())
                node_id_to_label_map = {
                    n["key"]: n["label"]
                    for n in content["dataModel"]["nodeLabels"].values()
                }
                return cls(
                    nodes=[
                        Node.from_solutions_workbench(SolutionsWorkbenchNode(**n))
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
        except Exception:
            raise InvalidSolutionsWorkbenchDataModelError(
                "Unable to parse the provided Solutions Workbench data model json file."
            )
