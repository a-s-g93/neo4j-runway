from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from pytest_mock import mocker

from neo4j_runway.exceptions import DataNotSupportedError
from neo4j_runway.utils.data import Table
from neo4j_runway.utils.data.data_dictionary.column import Column
from neo4j_runway.utils.data.data_dictionary.table_schema import TableSchema
from neo4j_runway.utils.data.data_loader import (
    _check_files,
    load_csv,
    load_json,
    load_local_files,
)

general_description = "people and pets"
table_schema_dict = {
    "name": "the name.",
    "age": "the age.",
    "pet": "the pet.",
    "city": "the city.",
}
table_schema = TableSchema(
    name="the name.",
    columns=[
        Column(name="age", description="the age."),
        Column(name="pet", description="the pet."),
        Column(name="city", description="the city."),
    ],
)
use_cases = ["Where are all the pets?"]


def test_load_csv_local() -> None:
    table: Table = load_csv(
        file_path="tests/resources/data/pets.csv",
        table_schema=table_schema,
        general_description=general_description,
        use_cases=use_cases,
    )

    assert (
        len(set(table.dataframe.columns).difference(set(table_schema_dict.keys()))) == 0
    )
    assert table.general_description == general_description
    assert table.use_cases == use_cases
    assert (
        len(
            set(table.table_schema.column_names).difference(
                set(table_schema_dict.keys())
            )
        )
        == 0
    )


def test_load_json_local() -> None:
    table: Table = load_json(
        file_path="tests/resources/data/pets.json",
        table_schema=table_schema,
        general_description=general_description,
        use_cases=use_cases,
    )

    assert (
        len(set(table.dataframe.columns).difference(set(table_schema_dict.keys()))) == 0
    )
    assert table.general_description == general_description
    assert table.use_cases == use_cases
    assert (
        len(
            set(table.table_schema.column_names).difference(
                set(table_schema_dict.keys())
            )
        )
        == 0
    )


def test_load_jsonl_local() -> None:
    table: Table = load_json(
        file_path="tests/resources/data/pets.jsonl",
        table_schema=table_schema,
        general_description=general_description,
        use_cases=use_cases,
    )

    assert (
        len(set(table.dataframe.columns).difference(set(table_schema_dict.keys()))) == 0
    )
    assert table.general_description == general_description
    assert table.use_cases == use_cases
    assert (
        len(
            set(table.table_schema.column_names).difference(
                set(table_schema_dict.keys())
            )
        )
        == 0
    )


def test_load_csv_with_config() -> None:
    config = {"usecols": ["name", "pet"], "sep": "|"}
    table: Table = load_csv(
        file_path="tests/resources/data/pets-piped.csv",
        table_schema=table_schema,
        general_description=general_description,
        use_cases=use_cases,
        config=config,
    )

    assert len(table.dataframe.columns) == 2
    assert table.general_description == general_description
    assert table.use_cases == use_cases
    assert (
        len(
            set(table.table_schema.column_names).difference(
                set(table_schema_dict.keys())
            )
        )
        == 0
    )


def test_load_csv_bad_table_schema() -> None:
    with pytest.raises(ValueError) as e:
        load_csv(
            file_path="tests/resources/data/pets.csv",
            table_schema=TableSchema(
                name="", columns=[Column(name="bad", description="")]
            ),
            general_description=general_description,
            use_cases=use_cases,
            config=dict(),
        )
    assert " but some do not exist in the data." in str(e.value)


def test_load_json_bad_table_schema() -> None:
    with pytest.raises(KeyError) as e:
        load_json(
            file_path="tests/resources/data/pets.json",
            table_schema=TableSchema(
                name="", columns=[Column(name="bad", description="")]
            ),
            general_description=general_description,
            use_cases=use_cases,
            config=dict(),
        )
    assert " but some do not exist in the data." in str(e.value)


def test_check_files_good_input() -> None:
    assert _check_files({"a.csv", "b.json", "c.jsonl"}) == True


def test_check_files_bad_input() -> None:
    with pytest.raises(DataNotSupportedError) as e:
        _check_files({"a.csv", "b.badext"})


def test_load_local_files_with_ignored(mocker) -> None:
    return_value = Table(
        name="test.csv",
        file_path="./",
        dataframe=pd.DataFrame({"a": [1, 2, 3], "b": [1, 2, 3], "c": [1, 2, 3]}),
        general_description=general_description,
        table_schema=table_schema,
        use_cases=use_cases,
        discovery_content=None,
    )
    mocker.patch(
        "neo4j_runway.utils.data.data_loader.load_csv", return_value=return_value
    )

    tables = load_local_files(
        data_directory="tests/resources/data/test_dir/",
        general_description=general_description,
        data_dictionary={"a.csv": table_schema_dict, "b.csv": table_schema_dict},
        use_cases=use_cases,
        ignored_files=["c.csv"],
    )

    assert len(tables.tables) == 2


def test_load_local_files_with_included(mocker) -> None:
    return_value = Table(
        name="test.csv",
        file_path="./",
        dataframe=pd.DataFrame({"a": [1, 2, 3], "b": [1, 2, 3], "c": [1, 2, 3]}),
        general_description=general_description,
        table_schema=table_schema,
        use_cases=use_cases,
        discovery_content=None,
    )
    mocker.patch(
        "neo4j_runway.utils.data.data_loader.load_csv", return_value=return_value
    )

    tables = load_local_files(
        data_directory="tests/resources/data/test_dir/",
        general_description=general_description,
        data_dictionary={"c.csv": table_schema_dict},
        use_cases=use_cases,
        include_files=["c.csv"],
    )

    assert len(tables.tables) == 1


def test_load_local_files_with_included_and_ignored(mocker) -> None:
    return_value = Table(
        name="test.csv",
        file_path="./",
        dataframe=pd.DataFrame({"a": [1, 2, 3], "b": [1, 2, 3], "c": [1, 2, 3]}),
        general_description=general_description,
        table_schema=table_schema,
        use_cases=use_cases,
        discovery_content=None,
    )
    mocker.patch(
        "neo4j_runway.utils.data.data_loader.load_csv", return_value=return_value
    )

    tables = load_local_files(
        data_directory="tests/resources/data/test_dir/",
        general_description=general_description,
        data_dictionary={"c.csv": table_schema_dict},
        use_cases=use_cases,
        include_files=["c.csv"],
        ignored_files=["a.csv", "c.csv"],
    )

    assert len(tables.tables) == 1
