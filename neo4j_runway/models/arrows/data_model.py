"""
This file contains the objects to construct a data model as it is represented in arrows.app.
"""

from typing import Dict, List, Any

from pydantic import BaseModel

from .node import ArrowsNode
from .relationship import ArrowsRelationship

DEFAULT_STYLE = {
    "font-family": "Nunito Sans",
    "background-color": "#F2F2F2",
    "background-image": "",
    "background-size": "100%",
    "node-color": "#4C8EDA",
    "border-width": 0,
    "border-color": "#000000",
    "radius": 75,
    "node-padding": 5,
    "node-margin": 2,
    "outside-position": "auto",
    "node-icon-image": "",
    "node-background-image": "",
    "icon-position": "inside",
    "icon-size": 64,
    "caption-position": "inside",
    "caption-max-width": 200,
    "caption-color": "#ffffff",
    "caption-font-size": 20,
    "caption-font-weight": "normal",
    "label-position": "inside",
    "label-display": "bare",
    "label-color": "#ffffff",
    "label-background-color": "#848484",
    "label-border-color": "#848484",
    "label-border-width": 3,
    "label-font-size": 20,
    "label-padding": 5,
    "label-margin": 4,
    "directionality": "directed",
    "detail-position": "above",
    "detail-orientation": "parallel",
    "arrow-width": 3,
    "arrow-color": "#848484",
    "margin-start": 5,
    "margin-end": 5,
    "margin-peer": 20,
    "attachment-start": "normal",
    "attachment-end": "normal",
    "relationship-icon-image": "",
    "type-color": "#848484",
    "type-background-color": "#F2F2F2",
    "type-border-color": "#848484",
    "type-border-width": 0,
    "type-font-size": 21,
    "type-padding": 5,
    "property-position": "outside",
    "property-alignment": "colon",
    "property-color": "#848484",
    "property-font-size": 20,
    "property-font-weight": "normal",
}


class ArrowsDataModel(BaseModel):
    """
    Data Model representation in arrows.app.
    """

    nodes: List[ArrowsNode]
    relationships: List[ArrowsRelationship]
    style: Dict[str, Any] = DEFAULT_STYLE

    @property
    def node_id_to_node_label_mapping(self) -> Dict[str, str]:
        return {node.id: node.labels[0] for node in self.nodes}
