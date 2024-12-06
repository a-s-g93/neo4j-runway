from typing import Any, Dict

import pytest

from neo4j_runway.utils.data.data_dictionary.column import Column
from neo4j_runway.utils.data.data_dictionary.table_schema import TableSchema


def test_init_good_no_validation_context() -> None:
    ts = TableSchema(
        name="table_a",
        columns=[Column(name="col_a", primary_key=True), Column(name="col_b")],
    )

    assert len(ts.columns) == 2


def test_init_good_with_validation_context(
    validation_info_context: Dict[str, Any],
) -> None:
    ts = TableSchema.model_validate(
        {
            "name": "table_a",
            "columns": [{"name": "col_a", "primary_key": True}, {"name": "col_b"}],
        },
        context=validation_info_context,
    )

    assert len(ts.columns) == 2


def test_init_many_primary_key_columns() -> None:
    with pytest.raises(ValueError):
        TableSchema(
            name="table_a",
            columns=[
                Column(name="col_a", primary_key=True),
                Column(name="col_b", primary_key=True),
            ],
        )


def test_column_names() -> None:
    ts = TableSchema(
        name="table_a",
        columns=[Column(name="col_a", primary_key=True), Column(name="col_b")],
    )

    assert len(ts.column_names) == 2


def test_primary_key() -> None:
    ts = TableSchema(
        name="table_a",
        columns=[Column(name="col_a", primary_key=True), Column(name="col_b")],
    )

    assert ts.primary_key.name == "col_a"


def test_primary_key_not_present() -> None:
    ts = TableSchema(
        name="table_a",
        columns=[Column(name="col_a", primary_key=False), Column(name="col_b")],
    )

    assert ts.primary_key is None


def test_foreign_keys() -> None:
    ts = TableSchema(
        name="table_a",
        columns=[
            Column(name="col_a", primary_key=False, foreign_key=True),
            Column(name="col_b", foreign_key=True),
        ],
    )

    assert len(ts.foreign_keys) == 2


def test_foreign_keys_empty() -> None:
    ts = TableSchema(
        name="table_a",
        columns=[Column(name="col_a", primary_key=True), Column(name="col_b")],
    )

    assert len(ts.foreign_keys) == 0


def test_compact_dict() -> None:
    ts = TableSchema(
        name="table_a",
        columns=[Column(name="col_a", primary_key=True), Column(name="col_b")],
    )

    assert len(ts.compact_dict.get(ts.name)) == 2
    assert ts.name in ts.compact_dict.keys()
    assert len(ts.compact_dict.keys()) == 1


def test_get_column_exists() -> None:
    ts = TableSchema(
        name="table_a",
        columns=[Column(name="col_a", primary_key=True), Column(name="col_b")],
    )

    assert ts.get_column("col_a") is not None


def test_get_column_not_exists() -> None:
    ts = TableSchema(
        name="table_a",
        columns=[Column(name="col_a", primary_key=True), Column(name="col_b")],
    )

    assert ts.get_column("error") is None
