"""
This file contains the functions to create indexes.
"""

from typing import Any, Dict, List

from ...models import Property


def generate_range_index(label_or_type: str, property: Property) -> str:
    """
    Generate a range index for a single property.
    """
    pass


def generate_composite_range_index(
    label_or_type: str, properties: List[Property]
) -> str:
    """
    Generate a composite range index for multiple properties.
    """
    pass


def generate_text_index(
    label_or_type: str, property: Property, config: Dict[str, Any]
) -> str:
    """
    Generate a text index on a single property. Property must be a STRING type.
    """
    pass


def generate_point_index(
    label_or_type: str, property: Property, config: Dict[str, Any]
) -> str:
    """
    Generate a point index on a single property. Property must be a POINT type.
    """
    pass


def generate_full_text_index(
    label_or_type: str, properties: List[Property], config: Dict[str, Any]
) -> str:
    """
    Generate a full text index on one or many properties. Properties must be of type STRING.
    """
    pass


def generate_vector_index(
    label_or_type: str, property: Property, config: Dict[str, Any]
) -> str:
    """
    Generate a vector index on a property. Property must be of type LIST<FLOAT>.
    """
    pass
