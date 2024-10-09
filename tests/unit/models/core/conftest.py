from typing import Any, Dict

import pytest


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
    data_dictionary = {
        "a.csv": {"id": "unique id for a. Has alias a_id", "b": "feature b"},
        "b.csv": {
            "id": "unique id for b",
            "a_id": "unique id for a.",
            "c": "feature c",
        },
    }
    return {
        "data_dictionary": data_dictionary,
        "valid_columns": {k: list(v.keys()) for k, v in data_dictionary.items()},
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
