from enum import Enum
from typing import List, Dict, Union, Any

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
    "unknown": "unknown"
}

TYPES_MAP_PYTHON_KEYS = {v: k for k, v in TYPES_MAP_NEO4J_KEYS.items()}


class Property(BaseModel):
    """
    Property representation.
    """

    name: str
    type: str
    csv_mapping: str
    is_unique: bool = False
    # is_indexed: bool
    # must_exist: bool

    def __init__(self, *a, **kw) -> None:
        super().__init__(*a, **kw)

    @field_validator("type")
    def validate_type(cls, v):
        if v == "object":
            return "str"
        if v not in list(TYPES_MAP_PYTHON_KEYS.keys()) + list(
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
