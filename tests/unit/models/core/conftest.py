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
