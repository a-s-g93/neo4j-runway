"""
This file contains a data model as it is represented in Solutions Workbench.
"""

import json
from typing import Any, Dict

from pydantic import BaseModel

from .node import SolutionsWorkbenchNode
from .relationship import SolutionsWorkbenchRelationship


class SolutionsWorkbenchDataModel(BaseModel):
    nodeLabels: Dict[str, SolutionsWorkbenchNode]
    relationshipTypes: Dict[str, SolutionsWorkbenchRelationship]
    metadata: Dict[str, Any] = dict()

    def model_dump_json(self, **kwargs: Any) -> str:
        """
        Overrides the Pydantic model_dump_json method.

        Returns
        -------
        str
            A JSON string representation of the model.
        """
        res = {
            "metadata": self.metadata,
            "dataModel": {
                "nodeLabels": self.nodeLabels_json,
                "relationshipTypes": self.relationshipTypes_json,
            },
        }

        return json.dumps(res, **kwargs)

    @property
    def nodeLabels_json(self) -> Dict[str, Dict[str, Any]]:
        return {k: v.model_dump() for (k, v) in self.nodeLabels.items()}

    @property
    def relationshipTypes_json(self) -> Dict[str, Dict[str, Any]]:
        return {k: v.model_dump() for (k, v) in self.relationshipTypes.items()}
