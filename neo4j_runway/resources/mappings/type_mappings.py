TYPES_MAP_NEO4J_TO_PYTHON = {
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
    "POINT": "neo4j.spatial.Point",
    "POINT Cartesian": "neo4j.spatial.CartesianPoint",
    "POINT WGS-84": "neo4j.spatial.WGS84Point",
    "unknown": "unknown",
}

TYPES_MAP_PYTHON_TO_NEO4J = {v: k for k, v in TYPES_MAP_NEO4J_TO_PYTHON.items()}

TYPES_MAP_SOLUTIONS_WORKBENCH_TO_PYTHON = {
    "String": "str",
    "Integer": "int",
    "Float": "float",
    "Boolean": "bool",
    "Date": "neo4j.time.Date",
    "Time": "neo4j.time.Time",
    "LocalTime": "neo4j.time.Time",
    "DateTime": "neo4j.time.DateTime",
    "LocalDateTime": "neo4j.time.DateTime",
    "Duration": "neo4j.time.Duration",
    "Point": "neo4j.spatial.Point",
    "String Array": "List<str>",
    "Integer Array": "List<int>",
    "Float Array": "List<float>",
    "Boolean Array": "List<bool>",
    "Date Array": "List<neo4j.time.Date>",
    "Time Array": "List<neo4j.time.Time>",
    "LocalTime Array": "List<neo4j.time.Time>",
    "DateTime Array": "List<neo4j.time.DateTime>",
    "LocalDateTime Array": "List<neo4j.time.DateTime>",
    "Duration Array": "List<neo4j.time.Duration>",
    "Point Array": "List<neo4j.spatial.Point>",
    "unknown": "unknown",
}

TYPES_MAP_PYTHON_TO_SOLUTIONS_WORKBENCH = {
    v: k for k, v in TYPES_MAP_SOLUTIONS_WORKBENCH_TO_PYTHON.items()
}
