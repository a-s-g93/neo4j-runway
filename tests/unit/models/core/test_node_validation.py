from typing import Any, Dict

import pytest
from pydantic import ValidationError

from neo4j_runway.models import Node


def test_validate_wrong_source_file_name_multifile(
    node_context: Dict[str, Any], node_data: Dict[str, Any]
) -> None:
    node_data["source_name"] = "wrong.csv"
    with pytest.raises(ValueError):
        Node.model_validate(node_data, context=node_context)


def test_validate_wrong_source_file_name_singlefile(node_data: Dict[str, Any]) -> None:
    assert node_data.get("source_name") == "a.csv"
    node = Node.model_validate(
        node_data, context={"valid_columns": {"b.csv": ["nkey"]}}
    )
    assert node.source_name == "b.csv"


def test_enforce_uniqueness_pass(
    node_context: Dict[str, Any], node_data: Dict[str, Any]
) -> None:
    assert node_context.get("enforce_uniqueness")
    Node.model_validate(node_data, context=node_context)


def test_enforce_uniqueness_fail(
    node_context: Dict[str, Any], node_data: Dict[str, Any]
) -> None:
    data = node_data
    data.get("properties")[0]["is_unique"] = False

    with pytest.raises(ValidationError):
        Node.model_validate(data, context=node_context)


def test_validate_property_mappings_one_prop(
    node_context: Dict[str, Any], node_data: Dict[str, Any]
) -> None:
    node_data["properties"] = [
        {
            "name": "nkey",
            "type": "str",
            "column_mapping": "wrong",
            "is_unique": True,
            "part_of_key": False,
        }
    ]
    with pytest.raises(ValidationError):
        Node.model_validate(node_data, context=node_context)


def test_validate_property_mappings_two_props(
    node_context: Dict[str, Any], node_data: Dict[str, Any]
) -> None:
    node_data["properties"] = [
        {
            "name": "nkey",
            "type": "str",
            "column_mapping": "wrong1",
            "is_unique": True,
            "part_of_key": False,
        },
        {
            "name": "nkey2",
            "type": "str",
            "column_mapping": "wrong2",
            "is_unique": True,
            "part_of_key": False,
        },
    ]
    with pytest.raises(ValidationError) as e:
        Node.model_validate(node_data, context=node_context)
    assert "wrong1" in str(e.value)
    assert "wrong2" in str(e.value)
