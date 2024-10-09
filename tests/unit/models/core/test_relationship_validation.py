from typing import Any, Dict

import pytest
from pydantic import ValidationError

from neo4j_runway.models.core.relationship import Relationship


def test_validate_wrong_source_file_name_multifile(
    relationship_context: Dict[str, Any], relationship_data: Dict[str, Any]
) -> None:
    relationship_data["source_name"] = "wrong.csv"
    with pytest.raises(ValueError):
        Relationship.model_validate(relationship_data, context=relationship_context)


def test_validate_wrong_source_file_name_singlefile(
    relationship_data: Dict[str, Any],
) -> None:
    assert relationship_data.get("source_name") == "a.csv"
    relationship = Relationship.model_validate(
        relationship_data, context={"valid_columns": {"b.csv": ["nkey"]}}
    )
    assert relationship.source_name == "b.csv"


def test_enforce_uniqueness_pass(
    relationship_context: Dict[str, Any], relationship_data: Dict[str, Any]
) -> None:
    assert relationship_context.get("enforce_uniqueness")
    Relationship.model_validate(relationship_data, context=relationship_context)


# Don't enforce relationship uniqueness feature at this time.
# def test_enforce_uniqueness_fail(relationship_context: Dict[str, Any], relationship_data: Dict[str, Any]) -> None:

#     data = relationship_data
#     data.get("properties")[0]["is_unique"] = False

#     with pytest.raises(ValidationError):
#         Relationship.model_validate(data, context=relationship_context)


def test_validate_property_mappings_one_prop(
    relationship_context: Dict[str, Any], relationship_data: Dict[str, Any]
) -> None:
    relationship_data["properties"] = [
        {
            "name": "nkey",
            "type": "str",
            "column_mapping": "wrong",
            "is_unique": True,
            "part_of_key": False,
        }
    ]
    with pytest.raises(ValidationError):
        Relationship.model_validate(relationship_data, context=relationship_context)


def test_validate_property_mappings_two_props(
    relationship_context: Dict[str, Any], relationship_data: Dict[str, Any]
) -> None:
    relationship_data["properties"] = [
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
        Relationship.model_validate(relationship_data, context=relationship_context)
    assert "wrong1" in str(e.value)
    assert "wrong2" in str(e.value)
