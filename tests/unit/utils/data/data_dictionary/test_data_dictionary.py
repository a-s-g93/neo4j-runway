from typing import Any, Dict

from neo4j_runway.utils.data.data_dictionary.data_dictionary import DataDictionary

table_a = {
    "name": "table_a",
    "columns": [
        {"name": "col_a", "primary_key": True},
        {"name": "col_b", "nullable": True},
    ],
}
table_b = {
    "name": "table_b",
    "columns": [
        {"name": "col_c", "primary_key": True, "python_type": "str"},
        {"name": "col_a_alias", "foreign_key": True},
    ],
}


def test_init_with_context(validation_info_context: Dict[str, Any]) -> None:
    DataDictionary.model_validate(
        {"table_schemas": [table_a, table_b]}, context=validation_info_context
    )


def test_compact_dict(validation_info_context: Dict[str, Any]) -> None:
    dd = DataDictionary.model_validate(
        {"table_schemas": [table_a, table_b]}, context=validation_info_context
    )

    assert len(dd.compact_dict.keys()) == 2

    assert {"table_a", "table_b"} == set(dd.compact_dict.keys())


def test_is_multifile_true(validation_info_context: Dict[str, Any]) -> None:
    dd = DataDictionary.model_validate(
        {"table_schemas": [table_a, table_b]}, context=validation_info_context
    )

    assert dd.is_multifile


def test_is_multifile_false(validation_info_context: Dict[str, Any]) -> None:
    dd = DataDictionary.model_validate(
        {"table_schemas": [table_a]}, context=validation_info_context
    )

    assert not dd.is_multifile
