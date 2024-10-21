import os

import pandas as pd

from neo4j_runway.discovery.discovery_content import DiscoveryContent

dc = DiscoveryContent(
    "general",
    pd.DataFrame({"a": [1, 2, 3]}),
    pd.DataFrame({"b": [4, 5, 6]}),
    "discovery",
)


def test_write_markdown() -> None:
    dc.to_markdown()

    with open("discovery.md") as f:
        data = f.read()

    os.remove("discovery.md")

    assert dc.discovery in data
    assert dc.pandas_general_description in data
    assert str(dc.pandas_categorical_description) in data
    assert str(dc.pandas_numerical_description) in data


def test_write_txt() -> None:
    dc.to_txt()

    with open("discovery.txt") as f:
        data = f.read()

    os.remove("discovery.txt")

    assert dc.discovery in data
    assert dc.pandas_general_description in data
    assert str(dc.pandas_categorical_description) in data
    assert str(dc.pandas_numerical_description) in data
