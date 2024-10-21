"""
This file contains the DataModel class which is the standard representation of a graph data model in Neo4j Runway.
"""

import json
from ast import literal_eval
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

import yaml
from graphviz import Digraph
from pydantic import (
    BaseModel,
    ValidationError,
    ValidationInfo,
    model_validator,
)
from pydantic_core import InitErrorDetails, PydanticCustomError

from ...exceptions import (
    InvalidArrowsDataModelError,
    InvalidSolutionsWorkbenchDataModelError,
)
from ..arrows import ArrowsDataModel, ArrowsNode, ArrowsRelationship
from ..solutions_workbench import (
    SolutionsWorkbenchDataModel,
    SolutionsWorkbenchNode,
    SolutionsWorkbenchRelationship,
)
from .node import Node
from .property import Property
from .relationship import Relationship
from .visualization import create_dot


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

    def get_schema(
        self,
        verbose: bool = True,
        neo4j_typing: bool = False,
        print_schema: bool = False,
    ) -> str:
        """
        Get the data model schema.

        Parameters
        ----------
        verbose : bool, optional
            Whether to provide more detail, by default True
        neo4j_typing : bool, optional
            Whether to use Neo4j types instead of Python types, by default False
        print_schema : bool, optional
            Whether to auto print the schema, by default False

        Returns
        -------
        str
            The schema
        """

        nodes = ""
        rels = ""

        for n in self.nodes:
            nodes += n.get_schema(verbose=verbose, neo4j_typing=neo4j_typing)
        for r in self.relationships:
            rels += r.get_schema(verbose=verbose, neo4j_typing=neo4j_typing)

        schema = f"""Nodes
{nodes}
Relationships
{rels}
"""
        if print_schema:
            print(schema)

        return schema

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

    @model_validator(mode="after")
    def advanced_validation(self, info: ValidationInfo) -> "DataModel":
        errors: List[InitErrorDetails] = list()

        def _retrieve_unique_property_with_missing_alias_or_node(
            node_label: str,
        ) -> Union[List[Property], Property, Node, str]:
            """
            Retrieve:
                The unique Property or Properties on a node that is missing an alias
                OR
                The Node of interest, if no Properties are unique
                OR
                An empty String if search fails
            """
            node = self.node_dict.get(node_label)
            if node is not None:
                props: List[Property] = node.unique_properties
                if len(props) > 1:
                    return props[0]

            return props or node or ""

        def _retrieve_duplicated_property(
            context: Tuple[str, str, int, str, int, str],
        ) -> Property:
            """Retrieve a `Property` in the data model that shares a `column_mapping` attribute."""

            prop: Property = self.__getattribute__(context[1])[context[2]].properties[
                context[4]
            ]
            return prop

        def _parse_duplicated_property_location(
            context: Tuple[str, str, int, str, int, str],
        ) -> Tuple[str, int, str, int]:
            """Parse the location of a duplicated property in the data model and return the location formatted for Pydantic Error reporting."""
            #            n or r     n or r idx   properties   prop idx
            return (context[1], context[2], context[3], context[4])

        def _validate_relationship_sources_and_targets() -> List[InitErrorDetails]:
            """
            * Validate the source and target of a relationship exist in the model nodes.
            * Validate same-node rels Node has named alias.
            * Validate file-spanning rels have source / target with appropriate named aliases.
            """

            data_dictionary: Optional[Dict[str, Any]] = (
                info.context.get("data_dictionary")
                if info.context is not None
                else None
            )
            errors: List[InitErrorDetails] = list()

            for rel in self.relationships:
                # validate exists
                if rel.source not in self.node_labels:
                    errors.append(
                        InitErrorDetails(
                            type=PydanticCustomError(
                                "missing_source_node_error",
                                f"The `Relationship` {rel.type} has the source {rel.source} which does not exist in generated `Node` labels {self.node_labels}.",
                            ),
                            loc=("relationships",),
                            input=rel,
                            ctx={},
                        )
                    )
                if rel.target not in self.node_labels:
                    errors.append(
                        InitErrorDetails(
                            type=PydanticCustomError(
                                "missing_target_node_error",
                                f"The `Relationship` {rel.type} has the target {rel.target} which does not exist in generated `Node` labels.",
                            ),
                            loc=("relationships",),
                            input=rel,
                            ctx={},
                        )
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
                            InitErrorDetails(
                                type=PydanticCustomError(
                                    "node_missing_property_with_alias_error",
                                    f"The `Relationship` {rel.type} has source and target of the same `Node` label {rel.source}. `Node` {rel.source} must have a `Property` with a declared `alias` attribute.",
                                ),
                                loc=("nodes",),
                                input=_retrieve_unique_property_with_missing_alias_or_node(
                                    node_label=rel.source
                                ),
                                ctx={},
                            )
                        )

                if data_dictionary is not None:
                    # validate rels that span across files
                    # use data dictionary here since aliases shouldn't be used in the data model
                    source_node = self.node_dict.get(rel.source)
                    target_node = self.node_dict.get(rel.target)

                    if (
                        source_node is not None
                        and rel.source_name != source_node.source_name
                    ):
                        for prop in source_node.unique_properties:
                            if (
                                prop.alias is None
                                and prop.column_mapping
                                not in data_dictionary[rel.source_name]
                            ):
                                errors.append(
                                    InitErrorDetails(
                                        type=PydanticCustomError(
                                            "relationship_source_node_unique_property_missing_alias_error",
                                            f"The source `Node` {source_node.label} and `Relationship` {rel.type} are from different files. `Property` {prop.name} on source `Node` {source_node.label} must have an `alias` attribute found in file {rel.source_name}.",
                                        ),
                                        loc=("nodes",),
                                        input=prop,
                                        ctx={},
                                    )
                                )
                            elif prop.alias not in data_dictionary[rel.source_name]:
                                errors.append(
                                    InitErrorDetails(
                                        type=PydanticCustomError(
                                            "relationship_source_file_missing_source_node_unique_property_alias_error",
                                            f"`Node` {source_node.label} `Property` {prop.name} is not found in the file {rel.source_name} by the alias {prop.alias}. `Property` `{prop.name}` on source `Node` {source_node.label} must has an `alias` in file {rel.source_name}. Reference the data dictionary for possible alias.",
                                        ),
                                        loc=("nodes",),
                                        input=prop,
                                        ctx={},
                                    )
                                )
                            # here we assume the column_mapping is the same across files
                            elif (
                                prop.alias is None
                                and prop.column_mapping
                                in data_dictionary[rel.source_name]
                            ):
                                prop.alias = prop.column_mapping

                    if (
                        target_node is not None
                        and rel.source_name != target_node.source_name
                    ):
                        for prop in target_node.unique_properties:
                            if (
                                prop.alias is None
                                and prop.alias not in data_dictionary[rel.source_name]
                            ):
                                errors.append(
                                    InitErrorDetails(
                                        type=PydanticCustomError(
                                            "relationship_target_node_unique_property_missing_alias_error",
                                            f"The target `Node` {target_node.label} and `Relationship` {rel.type} are from different files. `Property` {prop.name} on target `Node` {target_node.label} must have an `alias` attribute found in file {rel.source_name}.",
                                        ),
                                        loc=("nodes",),
                                        input=prop,
                                        ctx={},
                                    )
                                )
                            elif prop.alias not in data_dictionary[rel.source_name]:
                                errors.append(
                                    InitErrorDetails(
                                        type=PydanticCustomError(
                                            "relationship_source_file_missing_target_node_unique_property_alias_error",
                                            f"`Node` {target_node.label} `Property` {prop.name} is not found in the file {rel.source_name} by the alias {prop.alias}. `Property` `{prop.name}` on target `Node` {target_node.label} must has an `alias` in file {rel.source_name}. Reference the data dictionary for possible alias.",
                                        ),
                                        loc=("nodes",),
                                        input=prop,
                                        ctx={},
                                    )
                                )
                            # here we assume the column_mapping is the same across files
                            elif (
                                prop.alias is None
                                and prop.column_mapping
                                in data_dictionary[rel.source_name]
                            ):
                                prop.alias = prop.column_mapping

            return errors

        def _validate_column_mappings_used_only_once() -> List[InitErrorDetails]:
            """
            Validate that each column mapping is used no more than one time in the data model.
            This check may be skipped by providing `allow_duplicate_column_mappings` = True in the validation context.
            """

            allow_duplicate_column_mappings: bool = (
                info.context.get("allow_duplicate_column_mappings", False)
                if info.context is not None
                else False
            )
            errors: List[InitErrorDetails] = list()

            if not allow_duplicate_column_mappings:
                used_features: Dict[
                    str, Dict[str, List[Tuple[str, str, int, str, int, str]]]
                ] = dict()
                # --- used_features example ---
                # file to column to labels or types
                # {
                # "a.csv": {"feature_a": ["LabelA", "LabelB"]},
                # "b.csv": {"feature_b": ["LabelA", "LabelB"],
                #           "feature_c": ["LabelD"]},
                # "c.csv": {}
                # }
                # -----------------------------

                for node_idx, node in enumerate(self.nodes):
                    # init the file dictionary
                    if node.source_name not in used_features.keys():
                        used_features[node.source_name] = dict()
                    for prop_idx, prop in enumerate(node.properties):
                        if prop.column_mapping not in list(
                            used_features[node.source_name].keys()
                        ):
                            used_features[node.source_name][prop.column_mapping] = [
                                (
                                    node.label,
                                    "nodes",
                                    node_idx,
                                    "properties",
                                    prop_idx,
                                    "column_mapping",
                                )
                            ]
                        else:
                            used_features[node.source_name][prop.column_mapping].append(
                                (
                                    node.label,
                                    "nodes",
                                    node_idx,
                                    "properties",
                                    prop_idx,
                                    "column_mapping",
                                )
                            )

                for rel_idx, rel in enumerate(self.relationships):
                    # init the file dictionary
                    if rel.source_name not in used_features.keys():
                        used_features[rel.source_name] = dict()
                    for prop_idx, prop in enumerate(rel.properties):
                        if prop.column_mapping not in list(
                            used_features[rel.source_name].keys()
                        ):
                            used_features[rel.source_name][prop.column_mapping] = [
                                (
                                    rel.type,
                                    "relationships",
                                    rel_idx,
                                    "properties",
                                    prop_idx,
                                    "column_mapping",
                                )
                            ]
                        else:
                            used_features[rel.source_name][prop.column_mapping].append(
                                (
                                    rel.type,
                                    "relationships",
                                    rel_idx,
                                    "properties",
                                    prop_idx,
                                    "column_mapping",
                                )
                            )

                for source_name, feature_dict in used_features.items():
                    for prop_mapping, labels_or_types in feature_dict.items():
                        if len(labels_or_types) > 1:
                            for l_or_t in labels_or_types:
                                errors.append(
                                    InitErrorDetails(
                                        type=PydanticCustomError(
                                            "duplicate_property_in_data_model_error",
                                            f"The `Property` `column_mapping` {prop_mapping} from file {source_name} is used for {labels_or_types} in the data model. Each must use a different column as a `Property` attribute `column_mapping` instead. Find alternative `Property` `column_mapping` from the column options in the `source_name` file or remove.",
                                        ),
                                        loc=_parse_duplicated_property_location(
                                            context=l_or_t
                                        ),
                                        input=_retrieve_duplicated_property(
                                            context=l_or_t
                                        ),
                                        ctx={},
                                    )
                                )

            return errors

        def _validate_parallel_relationships() -> List[InitErrorDetails]:
            """Validate that there are no parallel relationships in the data model"""

            # if rel.source in other rel.targets
            # get other rel
            # if other rel.source == rel.target AND rel.source != rel.target
            # # then this is cyclic
            errors: List[InitErrorDetails] = list()

            allow_parallel_relationships: bool = (
                info.context.get("allow_parallel_relationships", False)
                if info.context is not None
                else False
            )

            if not allow_parallel_relationships:
                for i in range(0, len(self.relationships)):
                    if i < len(self.relationships) - 1:
                        for j in range(i + 1, len(self.relationships)):
                            # check parallel
                            if (
                                self.relationships[i].source
                                == self.relationships[j].source
                                and self.relationships[i].target
                                == self.relationships[j].target
                            ):
                                errors.append(
                                    InitErrorDetails(
                                        type=PydanticCustomError(
                                            "parallel_relationship_error",
                                            f"The `Relationship` {self.relationships[i].type} is in parallel with `Relationship` {self.relationships[j].type}. Remove one of these Relationships from `relationships`.",
                                        ),
                                        loc=("relationships", i),
                                        input=self.relationships[i],
                                        ctx={},
                                    )
                                )
                            elif (
                                self.relationships[i].source
                                == self.relationships[j].target
                                and self.relationships[i].target
                                == self.relationships[j].source
                            ):
                                errors.append(
                                    InitErrorDetails(
                                        type=PydanticCustomError(
                                            "parallel_relationship_error",
                                            f"The `Relationship` {self.relationships[i].type} is in parallel with `Relationship` {self.relationships[j].type}. Remove one of these Relationships from `relationships`.",
                                        ),
                                        loc=("relationships", i),
                                        input=self.relationships[i],
                                        ctx={},
                                    )
                                )

            return errors

        errors.extend(_validate_relationship_sources_and_targets())
        errors.extend(_validate_column_mappings_used_only_once())
        errors.extend(_validate_parallel_relationships())

        if errors:
            raise ValidationError.from_exception_data(
                title=self.__class__.__name__,
                line_errors=errors,
            )

        return self

    def visualize(
        self, detail_level: Literal[1, 2, 3] = 3, neo4j_typing: bool = False
    ) -> Digraph:
        """
        Visualize the data model using Graphviz. Requires that Graphviz is installed.

        Parameters
        ----------
        detail_level : Literal[1, 2, 3]
            The level of detail to include in the visual\n
                1: Node labels and Relationship types only\n
                2: Node labels, Relationship types and basic Property info\n
                3: Node labels, Relationship types and all Property info
        neo4j_typing : bool, optional
            Whether to use Neo4j types instead of Python types, by default False

        Returns
        -------
        Digraph
            The dot for visualization
        """

        try:
            return create_dot(
                nodes=self.nodes,
                relationships=self.relationships,
                detail_level=detail_level,
                neo4j_typing=neo4j_typing,
            )
        except Exception as e:
            print(
                f"Unable to visualize data model. Is `Graphviz` installed properly? Error: {e}"
            )

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
