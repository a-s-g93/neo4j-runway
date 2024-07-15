"""
This file contains a relationship as it is represented in arrows.app.
"""

from typing import Dict

from pydantic import BaseModel


class ArrowsRelationship(BaseModel):
    """
    Relationship representation in arrows.app.
    """

    id: str
    fromId: str
    toId: str
    type: str
    properties: Dict[str, str] = {}
    style: Dict[str, str] = {}
