import pytest

from neo4j_runway.llm.context import Context, create_context
from neo4j_runway.utils.data.data_dictionary.column import Column
from neo4j_runway.utils.data.data_dictionary.data_dictionary import DataDictionary
from neo4j_runway.utils.data.data_dictionary.table_schema import TableSchema

full_context_dict = {
    "data_dictionary": DataDictionary(
        table_schemas=[
            TableSchema(name="a.csv", columns=[Column(name="a"), Column(name="b")])
        ]
    ),
    "valid_columns": {"a.csv": ["a", "b"]},
    "enforce_uniqueness": False,
    "allow_duplicate_column_mappings": True,
    "allow_parallel_relationships": True,
}


def test_create_context_full_input() -> None:
    context = create_context(**full_context_dict)

    assert context.get("valid_columns").get("a.csv") == ["a", "b"]
    assert context.get("data_dictionary").table_column_names_dict.get("a.csv") == [
        "a",
        "b",
    ]
    assert not context.get("enforce_uniqueness")
    assert context.get("allow_duplicate_column_mappings")
    assert context.get("allow_parallel_relationships")


def test_create_context_no_allowed_columns() -> None:
    values = full_context_dict
    values.pop("valid_columns")

    context = create_context(**values)

    assert context.get("valid_columns").get("a.csv") == ["a", "b"]
    assert context.get("data_dictionary").table_column_names_dict.get("a.csv") == [
        "a",
        "b",
    ]
    assert not context.get("enforce_uniqueness")
    assert context.get("allow_duplicate_column_mappings")
    assert context.get("allow_parallel_relationships")


def test_create_context_data_dictionary_only() -> None:
    context = create_context(data_dictionary=full_context_dict.get("data_dictionary"))

    assert context.get("valid_columns").get("a.csv") == ["a", "b"]
    assert context.get("data_dictionary").table_column_names_dict.get("a.csv") == [
        "a",
        "b",
    ]
    assert context.get("enforce_uniqueness")
    assert not context.get("allow_duplicate_column_mappings")
    assert not context.get("allow_parallel_relationships")


def test_init_context_with_dictionary_instead_of_data_dictionary_object() -> None:
    with pytest.raises(AssertionError):
        create_context(
            data_dictionary={"a.csv": {"col_a": "description"}},
            valid_columns={"a.csv": ["col_a"]},
            enforce_uniqueness=True,
            allow_duplicate_column_mappings=False,
            allow_parallel_relationships=False,
        )
