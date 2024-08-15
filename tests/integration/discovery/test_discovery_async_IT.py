import pandas as pd
import pytest

from neo4j_runway.discovery import Discovery
from neo4j_runway.llm.openai import OpenAIDiscoveryLLM
from neo4j_runway.utils.data import Table, TableCollection

data_dict = {
    "a.csv": {"a": "numbers", "b": "more numbers"},
    "b.csv": {"c": "many more numbers", "d": "lots of numbers"},
    "c.csv": {"e": "letters", "f": "chars"},
}
t1 = Table(
    name="a.csv",
    file_path="./a.csv",
    data=pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]}),
    data_dictionary=data_dict["a.csv"],
    use_cases=["test discovery"],
)
t2 = Table(
    name="b.csv",
    file_path="./b.csv",
    data=pd.DataFrame({"c": [7, 8, 9], "d": [10, 11, 12]}),
    data_dictionary=data_dict["b.csv"],
    use_cases=["test discovery"],
)
t3 = Table(
    name="c.csv",
    file_path="./c.csv",
    data=pd.DataFrame({"e": ["a", "b", "c"], "f": ["d", "e", "f"]}),
    data_dictionary=data_dict["c.csv"],
    use_cases=["test discovery"],
)
table_collection = TableCollection(
    data_directory="./",
    data_dictionary=data_dict,
    data=[t1, t2, t3],
    general_description="contain data for testing discovery",
    use_cases=["test discovery"],
)

llm = OpenAIDiscoveryLLM(enable_async=True)


def test_single_table_run() -> None:
    d = Discovery(data=t1, llm=llm)

    d.run_async(show_result=False)

    assert d.data.discovery is not None
    assert d.data.data[0].discovery_content is not None
    assert d.data.data[0].discovery is not None


def test_multi_file_run() -> None:
    d = Discovery(data=table_collection, llm=llm)

    d.run_async(show_result=False)

    assert d.data.discovery is not None
    for t in d.data.data:
        assert t.discovery_content is not None
        assert t.discovery is not None
