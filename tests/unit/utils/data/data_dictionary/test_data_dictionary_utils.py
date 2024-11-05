from neo4j_runway.utils.data import (
    load_data_dictionary_from_compact_python_dictionary,
    load_data_dictionary_from_yaml,
    load_table_schema_from_compact_python_dictionary,
)


def test_multi_file_yaml_compact_dict() -> None:
    data_dict = load_data_dictionary_from_yaml(
        "tests/resources/configs/data_dictionary_multi.yaml"
    ).compact_dict

    assert "a.csv" in data_dict.keys()
    assert "b.csv" in data_dict.keys()
    assert "col_a" in data_dict["a.csv"].keys()
    assert "col_b" in data_dict["a.csv"].keys()
    assert "col_c" in data_dict["a.csv"].keys()
    assert (
        "The column of the letter being a Has aliases: ['feature_a']"
        in data_dict["a.csv"].values()
    )
    assert "The column of naming b" in data_dict["a.csv"].values()
    assert (
        "c is for column for which it has been named | ignore"
        in data_dict["a.csv"].values()
    )
    assert "col_e" in data_dict["b.csv"].keys()
    assert "col_d" in data_dict["b.csv"].keys()
    assert "col_f" in data_dict["b.csv"].keys()
    assert "column d" in data_dict["b.csv"].values()
    assert "column e" in data_dict["b.csv"].values()
    assert "column f | ignore" in data_dict["b.csv"].values()


def test_single_file_yaml_compact_dict() -> None:
    data_dict = load_data_dictionary_from_yaml(
        "tests/resources/configs/data_dictionary_single.yaml"
    ).compact_dict.get("a.csv", dict())

    assert "col_a" in data_dict.keys()
    assert "col_b" in data_dict.keys()
    assert "col_c" in data_dict.keys()
    assert (
        "The column of the letter being a Has aliases: ['feature_a']"
        in data_dict.values()
    )
    assert "The column of naming b" in data_dict.values()
    assert "c is for column for which it has been named | ignore" in data_dict.values()


def test_single_file_with_file_name_python_dict() -> None:
    dd = load_data_dictionary_from_compact_python_dictionary(
        {"a.csv": {"col_a": "desc a", "col_b": "desc b"}}
    )

    assert not dd.is_multifile
    assert len(dd.table_column_names_dict.get("a.csv")) == 2


def test_single_file_without_file_name_python_dict() -> None:
    dd = load_data_dictionary_from_compact_python_dictionary(
        {"col_a": "desc a", "col_b": "desc b"}
    )

    assert not dd.is_multifile
    assert len(dd.table_column_names_dict.get("file")) == 2


def test_multi_file_python_dict() -> None:
    dd = load_data_dictionary_from_compact_python_dictionary(
        {
            "a.csv": {"col_a": "desc a", "col_b": "desc b"},
            "b.csv": {"col_c": "desc c", "col_d": "desc d"},
        }
    )

    assert dd.is_multifile
    assert len(dd.table_schemas) == 2
    assert len(dd.table_column_names_dict.get("a.csv")) == 2
    assert len(dd.table_column_names_dict.get("b.csv")) == 2


def test_table_schema_with_file_name_python_dict() -> None:
    ts = load_table_schema_from_compact_python_dictionary(
        {"a.csv": {"col_a": "desc a", "col_b": "desc b"}}
    )

    assert ts.name == "a.csv"
    assert len(ts.column_names) == 2


def test_table_schema_without_file_name_python_dict() -> None:
    ts = load_table_schema_from_compact_python_dictionary(
        {"col_a": "desc a", "col_b": "desc b"}
    )

    assert ts.name == "file"
    assert len(ts.column_names) == 2
