import os

import pandas as pd

from neo4j_runway.utils.data import TableCollection


def test_write_markdown(
    table_collection_with_discovery_content: TableCollection,
) -> None:
    table_collection_with_discovery_content.to_markdown()

    with open("discovery.md") as f:
        data = f.read()

    os.remove("discovery.md")

    assert table_collection_with_discovery_content.discovery == data


def test_write_txt(table_collection_with_discovery_content: TableCollection) -> None:
    table_collection_with_discovery_content.to_txt()

    with open("discovery.txt") as f:
        data = f.read()

    os.remove("discovery.txt")

    assert table_collection_with_discovery_content.discovery == data
