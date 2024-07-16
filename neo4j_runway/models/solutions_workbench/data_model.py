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

    def model_dump_json(self) -> str:
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

        return json.dumps(res)

    # @property
    # def nodeLabels_json(self):
    #     return {k+str(i): v.model_dump() for i, (k, v) in enumerate(self.nodeLabels.items())}

    # @property
    # def relationshipTypes_json(self):
    #     return {k+str(i): v.model_dump() for i, (k, v) in enumerate(self.relationshipTypes.items())}

    @property
    def nodeLabels_json(self):
        return {k: v.model_dump() for (k, v) in self.nodeLabels.items()}

    @property
    def relationshipTypes_json(self):
        return {k: v.model_dump() for (k, v) in self.relationshipTypes.items()}
