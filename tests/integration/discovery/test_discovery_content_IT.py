import os

from neo4j_runway.discovery.discovery_content import DiscoveryContent


def test_write_markdown(discovery_content: DiscoveryContent) -> None:
    discovery_content.to_markdown()

    with open("discovery.md") as f:
        data = f.read()

    os.remove("discovery.md")

    assert discovery_content.discovery in data
    assert discovery_content.pandas_general_description in data
    assert str(discovery_content.pandas_categorical_description) in data
    assert str(discovery_content.pandas_numerical_description) in data


def test_write_txt(discovery_content: DiscoveryContent) -> None:
    discovery_content.to_txt()

    with open("discovery.txt") as f:
        data = f.read()

    os.remove("discovery.txt")

    assert discovery_content.discovery in data
    assert discovery_content.pandas_general_description in data
    assert str(discovery_content.pandas_categorical_description) in data
    assert str(discovery_content.pandas_numerical_description) in data
