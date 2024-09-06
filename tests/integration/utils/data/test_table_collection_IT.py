import os

import pandas as pd

from neo4j_runway.discovery.discovery_content import DiscoveryContent
from neo4j_runway.utils.data import Table, TableCollection

data_dict = {
    "a.csv": {"a": "numbers", "b": "more numbers"},
    "b.csv": {"c": "many more numbers", "d": "lots of numbers"},
    "c.csv": {"e": "letters", "f": "chars"},
}
dc = DiscoveryContent("general", pd.DataFrame(), pd.DataFrame(), "discovery")
t1 = Table(
    name="a.csv",
    file_path="./a.csv",
    dataframe=pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]}),
    data_dictionary=data_dict["a.csv"],
    use_cases=["test discovery"],
    discovery_content=dc,
)
t2 = Table(
    name="b.csv",
    file_path="./b.csv",
    dataframe=pd.DataFrame({"c": [7, 8, 9], "d": [10, 11, 12]}),
    data_dictionary=data_dict["b.csv"],
    use_cases=["test discovery"],
    discovery_content=dc,
)
t3 = Table(
    name="c.csv",
    file_path="./c.csv",
    dataframe=pd.DataFrame({"e": ["a", "b", "c"], "f": ["d", "e", "f"]}),
    data_dictionary=data_dict["c.csv"],
    use_cases=["test discovery"],
    discovery_content=dc,
)
table_collection = TableCollection(
    data_directory="./",
    data_dictionary=data_dict,
    tables=[t1, t2, t3],
    general_description="contain data for testing discovery",
    use_cases=["test discovery"],
    discovery="collection discovery",
)


def test_write_markdown() -> None:
    table_collection.to_markdown()

    with open("discovery.md") as f:
        data = f.read()

    os.remove("discovery.md")

    assert table_collection.discovery == data


def test_write_txt() -> None:
    table_collection.to_txt()

    with open("discovery.txt") as f:
        data = f.read()

    os.remove("discovery.txt")

    assert table_collection.discovery == data
