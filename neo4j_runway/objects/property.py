from enum import Enum
from typing import List, Dict, Union, Any, Self

from pydantic import BaseModel, field_validator


TYPES_MAP_NEO4J_KEYS = {
    "LIST": "list",
    "MAP": "dict",
    "BOOLEAN": "bool",
    "INTEGER": "int",
    "FLOAT": "float",
    "STRING": "str",
    "ByteArray": "bytearray",
    "DATE": "neo4j.time.Date",
    "ZONED TIME": "neo4j.time.Time",
    "LOCAL TIME": "neo4j.time.Time",
    "ZONED DATETIME": "neo4j.time.DateTime",
    "LOCAL DATETIME": "neo4j.time.DateTime",
    "DURATION": "neo4j.time.Duration",
    "POINT": "neo4j.spartial.Point",
    "POINT Cartesian": "neo4j.spartial.CartesianPoint",
    "POINT WGS-84": "neo4j.spartial.WGS84Point",
    "unknown": "unknown",
}

TYPES_MAP_PYTHON_KEYS = {v: k for k, v in TYPES_MAP_NEO4J_KEYS.items()}


class Property(BaseModel):
    """
    Property representation.
    """

    name: str
    type: str
    csv_mapping: Union[str, List[str]]
    is_unique: bool = False
    part_of_key: bool = False
    # is_indexed: bool
    # must_exist: bool

    @field_validator("type")
    def validate_type(cls, v):
        if v.lower() == "object" or v.lower() == "string":
            return "str"
        elif v.lower() == "float64":
            return "float"
        elif v.lower() == "int64":
            return "int"
        if v not in list(TYPES_MAP_PYTHON_KEYS.keys()) and v not in list(
            TYPES_MAP_PYTHON_KEYS.values()
        ):
            raise ValueError(f"{v} is an invalid type.")
        if v in list(TYPES_MAP_PYTHON_KEYS.values()):
            return TYPES_MAP_NEO4J_KEYS[v]
        return v

    @property
    def neo4j_type(self) -> str:
        """
        The Neo4j property type.
        """
        return TYPES_MAP_PYTHON_KEYS[self.type]

    @classmethod
    def from_arrows(cls, arrows_property: Dict[str, str], caption: str = "") -> Self:
        """
        Parse the arrows property representation into a standard Property model.
        Arrow property values are formatted as <csv_mapping> | <python_type> | <unique>.
        """

        if "|" in list(arrows_property.values())[0]:
            prop_props = [
                x.strip() for x in list(arrows_property.values())[0].split("|")
            ]
            if "," in prop_props[0]:
                csv_mapping: List[str] = [x.strip() for x in prop_props[0].split(",")]
            else:
                csv_mapping: str = prop_props[0]
            python_type = prop_props[1]
            is_unique = "unique" in prop_props
            node_key = "nodekey" in prop_props
        else:
            csv_mapping: str = list(arrows_property.values())[0]
            python_type = "unknown"
            is_unique = False
            node_key = False

        return cls(
            name=list(arrows_property.keys())[0],
            csv_mapping=csv_mapping,
            type=python_type,
            is_unique=is_unique,
            part_of_key=node_key,
        )
