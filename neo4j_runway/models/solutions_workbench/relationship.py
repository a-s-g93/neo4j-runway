"""
This file contains a relationship as it is represented in Solutions Workbench.
"""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel

from .property import SolutionsWorkbenchProperty

DEFAULT_DISPLAY = {
    "color": "black",
    "fontSize": 14,
    "strokeWidth": 3,
    "offset": 0,
    "glyph": None,
}


class SolutionsWorkbenchRelationship(BaseModel):
    """
    Relationship representation in Solutions Workbench.
    """

    classType: str = "RelationshipType"
    key: str
    description: str = ""
    type: str
    startNodeLabelKey: str
    endNodeLabelKey: str
    properties: Optional[Dict[str, SolutionsWorkbenchProperty]] = dict()
    referenceData: Optional[Dict[str, Any]] = dict()
    display: Dict[str, Any] = DEFAULT_DISPLAY
    outMinCardinality: str = "0"
    outMaxCardinality: str = "many"
    inMinCardinality: str = "0"
    inMaxCardinality: str = "many"
