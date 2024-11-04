from neo4j_runway.utils.data import load_data_dictionary_from_yaml


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
