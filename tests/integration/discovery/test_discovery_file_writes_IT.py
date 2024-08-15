import os

import pandas as pd
import pytest

from neo4j_runway.discovery import Discovery
from neo4j_runway.discovery.discovery_content import DiscoveryContent
from neo4j_runway.utils.data import Table, TableCollection

data_dict = {
    "a.csv": {"a": "numbers", "b": "more numbers"},
    "b.csv": {"c": "many more numbers", "d": "lots of numbers"},
    "c.csv": {"e": "letters", "f": "chars"},
}
dc = DiscoveryContent(
    "general",
    pd.DataFrame({"a": [1, 2, 3]}),
    pd.DataFrame({"b": [4, 5, 6]}),
    "discovery",
)
t1 = Table(
    name="a.csv",
    file_path="./a.csv",
    data=pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]}),
    data_dictionary=data_dict["a.csv"],
    use_cases=["test discovery"],
    discovery_content=dc,
)
t2 = Table(
    name="b.csv",
    file_path="./b.csv",
    data=pd.DataFrame({"c": [7, 8, 9], "d": [10, 11, 12]}),
    data_dictionary=data_dict["b.csv"],
    use_cases=["test discovery"],
    discovery_content=dc,
)
t3 = Table(
    name="c.csv",
    file_path="./c.csv",
    data=pd.DataFrame({"e": ["a", "b", "c"], "f": ["d", "e", "f"]}),
    data_dictionary=data_dict["c.csv"],
    use_cases=["test discovery"],
    discovery_content=dc,
)
table_collection = TableCollection(
    data_directory="./",
    data_dictionary=data_dict,
    data=[t1, t2, t3],
    general_description="contain data for testing discovery",
    use_cases=["test discovery"],
    discovery="final discovery",
)

d = Discovery(data=table_collection)

roots = ["a_discovery", "b_discovery", "c_discovery", "final_discovery"]


def test_write_txt_all() -> None:
    d.to_txt()

    for name in roots:
        with open(name + ".txt") as f:
            data = f.read()

        os.remove(name + ".txt")
        if not name.startswith("final"):
            assert dc.discovery in data
            assert dc.pandas_general_description in data
            assert str(dc.pandas_categorical_description) in data
            assert str(dc.pandas_numerical_description) in data
        else:
            assert "final discovery" in data


def test_write_markdown_all() -> None:
    d.to_markdown()

    for name in roots:
        with open(name + ".md") as f:
            data = f.read()

        os.remove(name + ".md")
        if not name.startswith("final"):
            assert dc.discovery in data
            assert dc.pandas_general_description in data
            assert str(dc.pandas_categorical_description) in data
            assert str(dc.pandas_numerical_description) in data
        else:
            assert "final discovery" in data


def test_write_txt_final() -> None:
    d.to_txt(file_name="final")

    with open("final_discovery.txt") as f:
        data = f.read()

    os.remove("final_discovery.txt")

    assert "final discovery" in data


def test_write_markdown_final() -> None:
    d.to_markdown(file_name="final")

    with open("final_discovery.md") as f:
        data = f.read()

    os.remove("final_discovery.md")

    assert "final discovery" in data


def test_write_txt_file() -> None:
    d.to_txt(file_name="a.csv")

    with open("a_discovery.txt") as f:
        data = f.read()

    os.remove("a_discovery.txt")

    assert dc.discovery in data
    assert dc.pandas_general_description in data
    assert str(dc.pandas_categorical_description) in data
    assert str(dc.pandas_numerical_description) in data


def test_write_markdown_file() -> None:
    d.to_markdown(file_name="a.csv")

    with open("a_discovery.md") as f:
        data = f.read()

    os.remove("a_discovery.md")

    assert dc.discovery in data
    assert dc.pandas_general_description in data
    assert str(dc.pandas_categorical_description) in data
    assert str(dc.pandas_numerical_description) in data


def test_write_txt_raise_error_no_file() -> None:
    with pytest.raises(ValueError):
        d.to_txt(file_name="bad.csv")


def test_write_markdown_raise_error_no_file() -> None:
    with pytest.raises(ValueError):
        d.to_markdown(file_name="bad.csv")
