from typing import Any, Dict

import pytest

from neo4j_runway.utils.data.data_dictionary.column import Column
from neo4j_runway.utils.data.data_dictionary.data_dictionary import DataDictionary
from neo4j_runway.utils.data.data_dictionary.table_schema import TableSchema


@pytest.fixture(scope="function")
def node_context() -> Dict[str, Any]:
    return {
        "valid_columns": {"a.csv": ["nkey"], "b.csv": ["col"]},
        "enforce_uniqueness": True,
    }


@pytest.fixture(scope="function")
def node_data() -> Dict[str, Any]:
    return {
        "label": "nodeA",
        "properties": [
            {
                "name": "nkey",
                "type": "str",
                "column_mapping": "nkey",
                "is_unique": True,
                "part_of_key": False,
            }
        ],
        "source_name": "a.csv",
    }


@pytest.fixture(scope="function")
def relationship_context() -> Dict[str, Any]:
    return {
        "valid_columns": {"a.csv": ["nkey"], "b.csv": ["col"]},
        "enforce_uniqueness": True,
    }


@pytest.fixture(scope="function")
def relationship_data() -> Dict[str, Any]:
    return {
        "type": "relA",
        "properties": [
            {
                "name": "nkey",
                "type": "str",
                "column_mapping": "nkey",
                "is_unique": True,
                "part_of_key": False,
            }
        ],
        "source_name": "a.csv",
        "source": "nodeA",
        "target": "nodeB",
    }


@pytest.fixture(scope="function")
def data_model_data() -> Dict[str, Any]:
    nodes = [
        {
            "label": "LabelA",
            "properties": [
                {
                    "name": "id",
                    "type": "str",
                    "column_mapping": "id",
                    "alias": "a_id",
                    "is_unique": True,
                },
                {"name": "b", "type": "str", "column_mapping": "b"},
            ],
            "source_name": "a.csv",
        },
        {
            "label": "LabelB",
            "properties": [
                {
                    "name": "id",
                    "type": "str",
                    "column_mapping": "id",
                    "is_unique": True,
                },
                {"name": "c", "type": "str", "column_mapping": "c"},
            ],
            "source_name": "b.csv",
        },
    ]

    return {
        "nodes": nodes,
        "relationships": [
            {
                "type": "HAS_REL",
                "source": "LabelA",
                "target": "LabelB",
                "source_name": "b.csv",
            }
        ],
    }


@pytest.fixture(scope="function")
def data_model_flipped_data() -> Dict[str, Any]:
    nodes = [
        {
            "label": "LabelA",
            "properties": [
                {
                    "name": "id",
                    "type": "str",
                    "column_mapping": "id",
                    "alias": "a_id",
                    "is_unique": True,
                },
                {"name": "b", "type": "str", "column_mapping": "b"},
            ],
            "source_name": "a.csv",
        },
        {
            "label": "LabelB",
            "properties": [
                {
                    "name": "id",
                    "type": "str",
                    "column_mapping": "id",
                    "is_unique": True,
                },
                {"name": "c", "type": "str", "column_mapping": "c"},
            ],
            "source_name": "b.csv",
        },
    ]

    return {
        "nodes": nodes,
        "relationships": [
            {
                "type": "HAS_REL",
                "source": "LabelB",
                "target": "LabelA",
                "source_name": "b.csv",
            }
        ],
    }


@pytest.fixture(scope="function")
def data_model_context() -> Dict[str, Any]:
    data_dictionary = DataDictionary(
        table_schemas=[
            TableSchema(
                name="a.csv",
                columns=[
                    Column(name="id", description="unique id for a.", aliases=["a_id"]),
                    Column(name="b", description="feature b"),
                ],
            ),
            TableSchema(
                name="b.csv",
                columns=[
                    Column(name="id", description="unique id for b."),
                    Column(name="a_id", description="unique id for a."),
                    Column(name="c", description="feature c"),
                ],
            ),
        ]
    )
    return {
        "data_dictionary": data_dictionary,
        "valid_columns": data_dictionary.table_column_names_dict,
        "enforce_uniqueness": True,
        "allow_duplicate_column_mappings": False,
    }


@pytest.fixture(scope="function")
def data_model_dupe_prop_data() -> Dict[str, Any]:
    nodes = [
        {
            "label": "LabelA",
            "properties": [
                {
                    "name": "id",
                    "type": "str",
                    "column_mapping": "id",
                    "is_unique": True,
                },
                {"name": "b", "type": "str", "column_mapping": "b"},
            ],
            "source_name": "a.csv",
        },
        {
            "label": "LabelB",
            "properties": [
                {
                    "name": "id",
                    "type": "str",
                    "column_mapping": "id",
                    "is_unique": True,
                },
            ],
            "source_name": "a.csv",
        },
    ]

    return {
        "nodes": nodes,
        "relationships": [
            {
                "type": "HAS_REL",
                "source": "LabelA",
                "target": "LabelB",
                "source_name": "a.csv",
            }
        ],
    }


@pytest.fixture(scope="function")
def data_model_parallel_data() -> Dict[str, Any]:
    nodes = [
        {
            "label": "LabelA",
            "properties": [
                {
                    "name": "id",
                    "type": "str",
                    "column_mapping": "id",
                    "alias": "a_id",
                    "is_unique": True,
                },
            ],
            "source_name": "a.csv",
        },
        {
            "label": "LabelB",
            "properties": [
                {
                    "name": "id2",
                    "type": "str",
                    "column_mapping": "id2",
                    "is_unique": True,
                },
            ],
            "source_name": "a.csv",
        },
    ]

    return {
        "nodes": nodes,
        "relationships": [
            {
                "type": "HAS_REL",
                "source": "LabelA",
                "target": "LabelB",
                "source_name": "a.csv",
            },
            {
                "type": "HAS_REL2",
                "source": "LabelA",
                "target": "LabelB",
                "source_name": "a.csv",
            },
        ],
    }


@pytest.fixture(scope="function")
def data_model_parallel_context() -> Dict[str, Any]:
    data_dictionary = DataDictionary(
        table_schemas=[
            TableSchema(
                name="a.csv",
                columns=[
                    Column(name="id", description="unique id for a.", aliases=["a_id"]),
                    Column(name="id2", description="unique id 2"),
                ],
            )
        ]
    )
    return {
        "data_dictionary": data_dictionary,
        "valid_columns": data_dictionary.table_column_names_dict,
        "enforce_uniqueness": True,
        "allow_duplicate_column_mappings": False,
        "allow_parallel_relationships": False,
    }


@pytest.fixture(scope="function")
def data_model_bad_context() -> Dict[str, Any]:
    data_dictionary = DataDictionary(
        table_schemas=[
            TableSchema(
                name="a.csv",
                columns=[
                    Column(name="id", description="unique id for a.", aliases=["a_id"]),
                    Column(name="b", description="feature b"),
                ],
            ),
            TableSchema(
                name="b.csv",
                columns=[
                    Column(name="id", description="unique id for b."),
                    Column(name="c", description="feature c"),
                ],
            ),
        ]
    )
    return {
        "data_dictionary": data_dictionary,
        "valid_columns": data_dictionary.table_column_names_dict,
        "enforce_uniqueness": True,
        "allow_duplicate_column_mappings": False,
        "allow_parallel_relationships": False,
    }
