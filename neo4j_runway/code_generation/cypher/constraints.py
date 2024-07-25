"""
This file contains the functions to create contraints.
"""

from typing import List, Union

from ...models import Property


def generate_constraints_key(
    label_or_type: str, unique_property: Union[Property, List[Property]]
) -> str:
    """
    Generate the key for a unique or node key constraint.
    """
    if isinstance(unique_property, Property):
        return f"{label_or_type.lower()}_{unique_property.name.lower()}"
    else:
        return f"{label_or_type.lower()}_{'_'.join([x.name.lower() for x in unique_property])}"


def generate_unique_constraint(label_or_type: str, unique_property: Property) -> str:
    """
    Generate a constraint string.
    """

    return f"CREATE CONSTRAINT {label_or_type.lower()}_{unique_property.name.lower()} IF NOT EXISTS FOR (n:{label_or_type}) REQUIRE n.{unique_property.name} IS UNIQUE;\n"


def generate_node_key_constraint(label: str, unique_properties: List[Property]) -> str:
    """
    Generate a node key constraint.
    """
    props = "(" + ", ".join([f"n.{x.name}" for x in unique_properties]) + ")"
    return f"""CREATE CONSTRAINT {generate_constraints_key(label_or_type=label, unique_property=unique_properties)} IF NOT EXISTS FOR (n:{label}) REQUIRE {props} IS NODE KEY;\n"""


def generate_relationship_key_constraint(
    type: str, unique_properties: List[Property]
) -> str:
    """
    Generate a relationship key constraint.
    """
    props = "(" + ", ".join([f"r.{x.name}" for x in unique_properties]) + ")"
    return f"""CREATE CONSTRAINT {generate_constraints_key(label_or_type=type, unique_property=unique_properties)} IF NOT EXISTS FOR ()-[r:{type}]-() REQUIRE {props} IS RELATIONSHIP KEY;\n"""
