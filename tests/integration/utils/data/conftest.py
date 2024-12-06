import pandas as pd
import pytest

from neo4j_runway.discovery.discovery_content import DiscoveryContent
from neo4j_runway.utils.data.data_dictionary.column import Column
from neo4j_runway.utils.data.data_dictionary.data_dictionary import DataDictionary
from neo4j_runway.utils.data.data_dictionary.table_schema import TableSchema
from neo4j_runway.utils.data.table import Table
from neo4j_runway.utils.data.table_collection import TableCollection


@pytest.fixture(scope="function")
def data_dictionary() -> DataDictionary:
    return DataDictionary(
        table_schemas=[
            TableSchema(
                name="a.csv",
                columns=[
                    Column(name="a", description="numbers"),
                    Column(name="b", description="more numbers"),
                ],
            ),
            TableSchema(
                name="b.csv",
                columns=[
                    Column(name="c", description="many more numbers"),
                    Column(name="d", description="lots of numbers"),
                ],
            ),
            TableSchema(
                name="c.csv",
                columns=[
                    Column(name="e", description="letters"),
                    Column(name="f", description="chars"),
                ],
            ),
        ]
    )


@pytest.fixture(scope="function")
def table_1(data_dictionary: DataDictionary) -> Table:
    return Table(
        name="a.csv",
        file_path="./a.csv",
        dataframe=pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]}),
        table_schema=data_dictionary.get_table_schema("a.csv"),
        use_cases=["test discovery"],
    )


@pytest.fixture(scope="function")
def table_2(data_dictionary: DataDictionary) -> Table:
    return Table(
        name="b.csv",
        file_path="./b.csv",
        dataframe=pd.DataFrame({"c": [7, 8, 9], "d": [10, 11, 12]}),
        table_schema=data_dictionary.get_table_schema("b.csv"),
        use_cases=["test discovery"],
    )


@pytest.fixture(scope="function")
def table_3(data_dictionary: DataDictionary) -> Table:
    return Table(
        name="c.csv",
        file_path="./c.csv",
        dataframe=pd.DataFrame({"e": ["a", "b", "c"], "f": ["d", "e", "f"]}),
        table_schema=data_dictionary.get_table_schema("c.csv"),
        use_cases=["test discovery"],
    )


@pytest.fixture(scope="function")
def discovery_content() -> DiscoveryContent:
    return DiscoveryContent(
        "general",
        pd.DataFrame({"a": [1, 2, 3]}),
        pd.DataFrame({"b": [4, 5, 6]}),
        "discovery",
    )


@pytest.fixture(scope="function")
def table_collection(
    table_1: Table, table_2: Table, table_3: Table, data_dictionary: DataDictionary
) -> TableCollection:
    return TableCollection(
        data_directory="./",
        data_dictionary=data_dictionary,
        tables=[table_1, table_2, table_3],
        general_description="contain data for testing discovery",
        use_cases=["test discovery"],
    )


@pytest.fixture(scope="function")
def table_collection_with_discovery_content(
    table_1: Table,
    table_2: Table,
    table_3: Table,
    data_dictionary: DataDictionary,
    discovery_content: DiscoveryContent,
) -> TableCollection:
    table_1.discovery_content = discovery_content
    table_2.discovery_content = discovery_content
    table_3.discovery_content = discovery_content

    return TableCollection(
        data_directory="./",
        data_dictionary=data_dictionary,
        tables=[table_1, table_2, table_3],
        general_description="contain data for testing discovery",
        use_cases=["test discovery"],
        discovery="final discovery",
    )
