"""
This file contains a node as it is represented in Solutions Workbench.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, computed_field

from .property import SolutionsWorkbenchProperty

default_display = {
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
    # display: Dict[str, Any] = default_display
    secondaryNodeLabelKeys: List[str] = list()
    isOnlySecondaryNodeLabel: bool = False
    referenceData: str = ""
    hasAnnotation: bool = False
    x: Optional[int] = None
    y: Optional[int] = None

    @computed_field
    @property
    def display(self) -> Dict[str, Any]:
        if self.x and self.y:
            default_display.update({"x": self.x, "y": self.y})
        return default_display
