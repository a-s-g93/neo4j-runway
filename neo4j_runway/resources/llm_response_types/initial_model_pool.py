from dataclasses import dataclass
from typing import Any, Dict, List

from pydantic import BaseModel

from ..prompts.data_modeling import (
    create_retry_initial_data_model_prep_generation_prompt,
)


@dataclass
class EntityPoolNode:
    label: str
    properties: List[str]
    explanation: str


@dataclass
class EntityPoolRelationship:
    type: str
    possible_sources: List[str]
    possible_targets: List[str]
    properties: List[str]
    explantation: str


class DataModelEntityPool(BaseModel):

    nodes: List[EntityPoolNode]
    relationships: List[EntityPoolRelationship]
    explanation: str

    def validate(self, allowed_features: List[str]) -> Dict[str, Any]:
        """
        Validate that all generated properties exist in the allowed features.

        Parameters
        ----------
        allowed_features : List[str]
            Features that exist in the data.

        Returns
        -------
        Dict[str, Any]
            return {"valid": bool, "message": str, "errors": List[str]}
        """

        errors: List[str] = list()

        for node in self.nodes:
            for prop in node.properties:
                if prop not in allowed_features:
                    errors.append(
                        f"The node {node.label} has the property {prop} which does not exist in the allowed features. {prop} should be removed or replaced from node {node.label}."
                    )
        for rel in self.relationships:
            for prop in rel.properties:
                if prop not in allowed_features:
                    errors.append(
                        f"The relationship {rel.type} has the property {prop} which does not exist in the allowed features. {prop} should be removed or replaced from relationship {rel.type}."
                    )

        for rel in self.relationships:
            # validate exists
            invalid_sources = set(rel.possible_sources) - {n.label for n in self.nodes}
            if len(invalid_sources) > 0:
                errors.append(
                    f"The relationship {rel.type} has the sources {invalid_sources} which do not exist in generated Node labels."
                )
            invalid_targets = set(rel.possible_targets) - {n.label for n in self.nodes}
            if len(invalid_targets) > 0:
                errors.append(
                    f"The relationship {rel.type} has the targets {invalid_targets} which do not exist in generated Node labels."
                )

        valid: bool = len(errors) == 0
        message = ""
        if not valid:
            message = create_retry_initial_data_model_prep_generation_prompt(
                invalid_options=self.model_dump(), errors=errors
            )

        return {"valid": valid, "message": message, "errors": errors}
