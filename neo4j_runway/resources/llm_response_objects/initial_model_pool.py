from dataclasses import dataclass
from typing import Any, Dict, List

from pydantic import BaseModel

from ..prompts import create_retry_initial_data_model_prep_generation_prompt


@dataclass
class EntityPoolNode:
    label: str
    properties: List[str]


@dataclass
class EntityPoolRelationship:
    type: str
    properties: List[str]


class DataModelEntityPool(BaseModel):

    nodes: List[EntityPoolNode]
    relationships: List[EntityPoolRelationship]

    def validate_properties(self, allowed_features: List[str]) -> Dict[str, Any]:
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

        valid: bool = len(errors) == 0
        message = ""
        if not valid:
            message = create_retry_initial_data_model_prep_generation_prompt(
                invalid_options=self.model_dump(), errors=errors
            )

        return {"valid": valid, "message": message, "errors": errors}
