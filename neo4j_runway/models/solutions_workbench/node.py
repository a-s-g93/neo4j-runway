"""
This file contains a node as it is represented in Solutions Workbench.
"""

from typing import Any, Dict, List

from pydantic import BaseModel

from .property import SolutionsWorkbenchProperty

DEFAULT_DISPLAY = {
    "color": "white",
    "stroke": "black",
    "strokeWidth": 4,
    "x": 540,
    "y": 340,
    "radius": 40,
    "size": "md",
    "width": 80,
    "height": 80,
    "fontSize": 14,
    "fontColor": "black",
    "textLocation": "middle",
    "isLocked": False,
    "glyphs": [],
}


class SolutionsWorkbenchNode(BaseModel):
    """
    Node representation in Solutions Workbench.
    """

    classType: str = "NodeLabel"
    key: str
    description: str = ""
    label: str
    fromDataSources: List[str] = list()
    indexes: List[Dict[str, Any]] = list()
    properties: Dict[str, SolutionsWorkbenchProperty] = dict()
    display: Dict[str, Any] = DEFAULT_DISPLAY
    secondaryNodeLabelKeys: List[str] = list()
    isOnlySecondaryNodeLabel: bool = False
    referenceData: str = ""
    hasAnnotation: bool = False
    x: int
    y: int
