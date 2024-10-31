"""Type mappings for Python and Neo4j

Python Date, Time, DateTime and spatial types are from the `neo4j` library.
They are found with the following prefixes:
* Date, Time, DateTime: `neo4j.time._`
* CartesianPoint, WGS84Point, Point: `neo4j.spatial._`
"""

from enum import Enum


class PythonTypeEnum(Enum):
    LIST = "List"
    DICT = "Dict"
    BOOL = "bool"
    INT = "int"
    FLOAT = "float"
    STR = "str"
    BYTEARRAY = "bytearray"
    DATE = "Date"
    TIME = "Time"
    DATETIME = "DateTime"
    DURATION = "Duration"
    POINT = "Point"
    CARTESIAN_POINT = "CartesianPoint"
    WGS84_POINT = "WGS84Point"
    UNKNOWN = "unknown"
    LIST_BOOL = "List[bool]"
    LIST_INT = "List[int]"
    LIST_FLOAT = "List[float]"
    LIST_STR = "List[str]"
    LIST_DATE = "List[Date]"
    LIST_DATETIME = "List[DateTime]"
    LIST_DURATION = "List[Duration]"
    LIST_POINT = "List[Point]"


TYPES_MAP_NEO4J_TO_PYTHON = {
    "LIST": "List",
    "MAP": "Dict",
    "BOOLEAN": "bool",
    "INTEGER": "int",
    "FLOAT": "float",
    "STRING": "str",
    "ByteArray": "bytearray",
    "DATE": "Date",
    "ZONED TIME": "Time",
    "LOCAL TIME": "Time",
    "ZONED DATETIME": "DateTime",
    "LOCAL DATETIME": "DateTime",
    "DURATION": "Duration",
    "POINT": "Point",
    "POINT Cartesian": "CartesianPoint",
    "POINT WGS-84": "WGS84Point",
    "unknown": "unknown",
}

TYPES_MAP_PYTHON_TO_NEO4J = {v: k for k, v in TYPES_MAP_NEO4J_TO_PYTHON.items()}

TYPES_MAP_SOLUTIONS_WORKBENCH_TO_PYTHON = {
    "String": "str",
    "Integer": "int",
    "Float": "float",
    "Boolean": "bool",
    "Date": "Date",
    "Time": "Time",
    "LocalTime": "Time",
    "DateTime": "DateTime",
    "LocalDateTime": "DateTime",
    "Duration": "Duration",
    "Point": "Point",
    "String Array": "List[str]",
    "Integer Array": "List[int]",
    "Float Array": "List[float]",
    "Boolean Array": "List[bool]",
    "Date Array": "List[Date]",
    "Time Array": "List[Time]",
    "LocalTime Array": "List[Time]",
    "DateTime Array": "List[DateTime]",
    "LocalDateTime Array": "List[DateTime]",
    "Duration Array": "List[Duration]",
    "Point Array": "List[Point]",
    "unknown": "unknown",
}

TYPES_MAP_PYTHON_TO_SOLUTIONS_WORKBENCH = {
    v: k for k, v in TYPES_MAP_SOLUTIONS_WORKBENCH_TO_PYTHON.items()
}
