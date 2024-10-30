from typing import Any, Dict

import pytest
from pydantic import ValidationError

from neo4j_runway.models import DataModel


def test_multi_file_different_source_relationship_valid_source_node(
    data_model_data: Dict[str, Any], data_model_context: Dict[str, Any]
) -> None:
    DataModel.model_validate(data_model_data, context=data_model_context)


def test_multi_file_different_source_relationship_valid_target_node(
    data_model_flipped_data: Dict[str, Any], data_model_context: Dict[str, Any]
) -> None:
    DataModel.model_validate(data_model_flipped_data, context=data_model_context)


def test_multi_file_different_source_relationship_invalid(
    data_model_data: Dict[str, Any], data_model_context: Dict[str, Any]
) -> None:
    data_dictionary_bad = {
        "a.csv": {"id": "unique id for a. Has alias a_id", "b": "feature b"},
        "b.csv": {"id": "unique id for b", "c": "feature c"},
    }
    valid_columns_bad = {k: list(v.keys()) for k, v in data_dictionary_bad.items()}

    data_model_context["data_dictionary"] = data_dictionary_bad
    data_model_context["valid_columns"] = valid_columns_bad

    with pytest.raises(ValidationError) as e:
        DataModel.model_validate(data_model_data, context=data_model_context)

    assert (
        "relationship_source_file_missing_source_node_unique_property_alias_error"
        in str(e.value)
    )


def test_allow_duplicate_properties_true(
    data_model_dupe_prop_data: Dict[str, Any], data_model_context: Dict[str, Any]
) -> None:
    data_model_context["allow_duplicate_column_mappings"] = True

    DataModel.model_validate(data_model_dupe_prop_data, context=data_model_context)


def test_allow_duplicate_properties_false(
    data_model_dupe_prop_data: Dict[str, Any], data_model_context: Dict[str, Any]
) -> None:
    with pytest.raises(ValidationError) as e:
        DataModel.model_validate(data_model_dupe_prop_data, context=data_model_context)

    assert "duplicate_property_in_data_model_error" in str(e.value)


def test_node_field_validator_error(
    data_model_data: Dict[str, Any], data_model_context: Dict[str, Any]
) -> None:
    data_model_data["nodes"][0]["file_name"] = "wrongfile.csv"

    with pytest.raises(ValueError) as e:
        DataModel.model_validate(data_model_data, context=data_model_context)

    assert "wrongfile.csv is not in the provided file list: ['a.csv', 'b.csv']." in str(
        e.value
    )


def test_node_model_validator_error(
    data_model_data: Dict[str, Any], data_model_context: Dict[str, Any]
) -> None:
    data_model_data["nodes"][0]["properties"] = [
        {
            "name": "nkey",
            "type": "str",
            "column_mapping": "wrong_mapping",
            "is_unique": True,
            "part_of_key": False,
        }
    ]
    with pytest.raises(ValueError) as e:
        DataModel.model_validate(data_model_data, context=data_model_context)

    assert "invalid_column_mapping_error" in str(e.value)


def test_relationship_field_validator_error(
    data_model_data: Dict[str, Any], data_model_context: Dict[str, Any]
) -> None:
    data_model_data["relationships"][0]["file_name"] = "wrongfile.csv"

    with pytest.raises(ValueError) as e:
        DataModel.model_validate(data_model_data, context=data_model_context)

    assert "wrongfile.csv is not in the provided file list: ['a.csv', 'b.csv']." in str(
        e.value
    )


def test_relationship_model_validator_error(
    data_model_data: Dict[str, Any], data_model_context: Dict[str, Any]
) -> None:
    data_model_data["relationships"][0]["properties"] = [
        {
            "name": "nkey",
            "type": "str",
            "column_mapping": "wrong_mapping",
            "is_unique": False,
            "part_of_key": False,
        }
    ]
    with pytest.raises(ValueError) as e:
        DataModel.model_validate(data_model_data, context=data_model_context)

    assert "invalid_column_mapping_error" in str(e.value)


def test_node_property_field_validator_error(
    data_model_data: Dict[str, Any], data_model_context: Dict[str, Any]
) -> None:
    data_model_data["relationships"][0]["properties"] = [
        {
            "name": "nkey",
            "type": "wrong_type",
            "column_mapping": "nkey",
            "is_unique": False,
            "part_of_key": False,
        }
    ]
    with pytest.raises(ValueError) as e:
        DataModel.model_validate(data_model_data, context=data_model_context)

    assert "Invalid Property type given: wrong_type" in str(e.value)


def test_allow_parallel_relationships_same_direction(
    data_model_parallel_data: Dict[str, Any],
    data_model_parallel_context: Dict[str, Any],
) -> None:
    with pytest.raises(ValidationError) as e:
        DataModel.model_validate(
            data_model_parallel_data, context=data_model_parallel_context
        )

    assert "parallel_relationship_error" in str(e.value)


def test_allow_parallel_relationships_opposite_direction(
    data_model_parallel_data: Dict[str, Any],
    data_model_parallel_context: Dict[str, Any],
) -> None:
    data_model_parallel_data["relationships"][0]["source"] = "LabelB"
    data_model_parallel_data["relationships"][0]["target"] = "LabelA"

    with pytest.raises(ValidationError) as e:
        DataModel.model_validate(
            data_model_parallel_data, context=data_model_parallel_context
        )

    assert "parallel_relationship_error" in str(e.value)


def test_ignore_parallel_relationships(
    data_model_parallel_data: Dict[str, Any],
    data_model_parallel_context: Dict[str, Any],
) -> None:
    data_model_parallel_context["allow_parallel_relationships"] = True

    DataModel.model_validate(
        data_model_parallel_data, context=data_model_parallel_context
    )
