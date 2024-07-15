"""
This file contains a node as it is represented in arrows.app.
"""

from typing import Dict, List
import warnings

from pydantic import BaseModel, field_validator


class ArrowsNode(BaseModel):
    """
    Node representation in arrows.app.
    """

    id: str
    position: Dict[str, float]
    caption: str = ""
    labels: List[str]
    properties: Dict[str, str] = {}
    style: Dict[str, str] = {}

    @field_validator("position")
    def validate_position(cls, v):
        if set(v.keys()) != {"x", "y"}:
            raise ValueError("position must have format: {'x': <float>, 'y': <float>}")
        return v

    @field_validator("labels")
    def validate_labels(cls, v):
        if len(v) > 1:
            warnings.warn(
                f"Multiple labels detected in Arrows model, but Runway only currently supports single node labels. Input: {v}, Runway model will use {v[0]}."
            )
        return v
