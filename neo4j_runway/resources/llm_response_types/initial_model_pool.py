from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from ..prompts.data_modeling import (
    create_retry_initial_data_model_prep_generation_prompt,
)


@dataclass
class EntityPoolProperty:
    name: str
    alias: Optional[str] = None


@dataclass
class EntityPoolNode:
    label: str
    properties: List[EntityPoolProperty]
    explanation: str
    source_name: str = "file"


@dataclass
class EntityPoolRelationship:
    type: str
    source: str
    target: str
    properties: List[EntityPoolProperty]
    explantation: str
    source_name: str = "file"


class DataModelEntityPool(BaseModel):
    nodes: List[EntityPoolNode]
    relationships: List[EntityPoolRelationship]
    explanation: str

    @property
    def node_dict(self) -> Dict[str, EntityPoolNode]:
        return {n.label: n for n in self.nodes}

    def validate_pool(
        self,
        valid_columns: Dict[str, List[str]],
        data_dictionary: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Validate that all generated properties exist in the allowed features.

        Parameters
        ----------
        valid_columns : List[str]
            Features that exist in the data.

        Returns
        -------
        Dict[str, Any]
            return {"valid": bool, "message": str, "errors": List[str]}
        """

        errors: List[str] = list()

        print(f"nodes : {[n.label for n in self.nodes]}")
        print(f"rels  : {[n.type for n in self.relationships]}")
        for node in self.nodes:
            if (
                not len(valid_columns.keys()) == 1
                and not node.source_name in valid_columns.keys()
            ):
                errors.append(
                    f"Node {node.label} has source_name {node.source_name} which is not in the provided file list: {list(valid_columns.keys())}."
                )

            for prop in node.properties:
                if prop.name not in valid_columns.get(node.source_name, list()):
                    errors.append(
                        f"The node {node.label} has the property {prop.name} which does not exist in {node.source_name}. {prop.name} should be removed or replaced from node {node.label}."
                    )
        for rel in self.relationships:
            if (
                not len(valid_columns.keys()) == 1
                and not rel.source_name in valid_columns.keys()
            ):
                errors.append(
                    f"Relationship {rel.type} has source_name {node.source_name} which is not in the provided file list: {list(valid_columns.keys())}."
                )

            for prop in rel.properties:
                if prop.name not in valid_columns.get(rel.source_name, list()):
                    errors.append(
                        f"The relationship {rel.type} has the property {prop.name} which does not exist in {rel.source_name}. {prop.name} should be removed or replaced from relationship {rel.type}."
                    )

        for rel in self.relationships:
            # validate exists
            # invalid_sources = {rel.source} - {n.label for n in self.nodes}
            if rel.source not in [n.label for n in self.nodes]:
                errors.append(
                    # f"The relationship {rel.type} has the possible source node {rel.source} which is not in the generated EntityPoolNode labels. Create an EntityPoolNode with label {rel.source}."
                    f"Create an EntityPoolNode with label {rel.source}."
                )

            # invalid_targets = {rel.target} - {n.label for n in self.nodes}
            if rel.target not in [n.label for n in self.nodes]:
                errors.append(
                    # f"The relationship {rel.type} has the possible target node {rel.target} which is not in the generated EntityPoolNode labels. Create an EntityPoolNode with label {rel.target}."
                    f"Create an EntityPoolNode with label {rel.target}."
                )

            # validate rels that span across files
            # use data dictionary here since aliases shouldn't be used in the data model
            source_node: Optional[EntityPoolNode] = self.node_dict.get(rel.source)
            target_node: Optional[EntityPoolNode] = self.node_dict.get(rel.target)

            if source_node is not None and rel.source_name != source_node.source_name:
                for prop in source_node.properties:
                    if prop.alias is not None and prop.alias not in data_dictionary.get(
                        rel.source_name, list()
                    ):
                        errors.append(
                            f"Node `{source_node.label}` Property `{prop.name}` is not found in the file `{rel.source_name}` by the name `{prop.alias}`. Find an alias for property `{prop.name}` on source node `{source_node.label}` in file `{rel.source_name}` and identify it on the Property attribute `alias` or remove this alias. Reference the data dictionary."
                        )

            if target_node is not None and rel.source_name != target_node.source_name:
                for prop in target_node.properties:
                    if prop.alias is not None and prop.alias not in data_dictionary.get(
                        rel.source_name, list()
                    ):
                        errors.append(
                            f"Node `{target_node.label}` Property `{prop.name}` is not found in the file `{rel.source_name}` by the name `{prop.alias}`. Find an alias for property `{prop.name}` on target node `{target_node.label}` in file `{rel.source_name}` and identify it on the Property attribute `alias` or remove this alias. Reference the data dictionary."
                        )

        valid: bool = len(errors) < 1
        message = ""
        if not valid:
            message = create_retry_initial_data_model_prep_generation_prompt(
                invalid_options=self,
                errors=errors,
                multifile=len(valid_columns.keys()) > 1,
                data_dictionary=data_dictionary,
                valid_columns=valid_columns,
            )

        return {"valid": valid, "message": message, "errors": errors}
