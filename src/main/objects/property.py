from enum import Enum
from typing import List, Dict, Union, Any

from pydantic import BaseModel, field_validator


PYTHON_TYPES = ["list", "str", "bool", "int", "float", "bytearray", "date", "datetime"]

TYPES_MAP = {
    "list": "LIST",
    "str": "STRING",
    "bool": "BOOLEAN",
    "int": "INTEGER",
    "float": "FLOAT",
    "bytearray": "ByteArray",
    "date": "date",
    "datetime": "datetime"


}
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

    @field_validator('type')
    def validate_type(cls, v):
        if v not in PYTHON_TYPES:
            raise ValueError(f'{v} is an invalid type.')
        return v
    
    @property
    def neo4j_type(self) -> str:
        """
        The Neo4j property type.
        """
        return TYPES_MAP[self.type]


    
