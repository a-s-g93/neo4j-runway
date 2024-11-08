import os

import pandas as pd
import pytest

from neo4j_runway.discovery import Discovery
from neo4j_runway.discovery.discovery_content import DiscoveryContent

roots = ["a_discovery", "b_discovery", "c_discovery", "final_discovery"]


def test_write_txt_all(
    discovery_with_discovery_content: Discovery, discovery_content: DiscoveryContent
) -> None:
    discovery_with_discovery_content.to_txt()

    for name in roots:
        with open(name + ".txt") as f:
            data = f.read()

        os.remove(name + ".txt")
        if not name.startswith("final"):
            assert discovery_content.discovery in data
            assert discovery_content.pandas_general_description in data
            assert str(discovery_content.pandas_categorical_description) in data
            assert str(discovery_content.pandas_numerical_description) in data
        else:
            assert "final discovery" in data


def test_write_markdown_all(
    discovery_with_discovery_content: Discovery, discovery_content: DiscoveryContent
) -> None:
    discovery_with_discovery_content.to_markdown()

    for name in roots:
        with open(name + ".md") as f:
            data = f.read()

        os.remove(name + ".md")
        if not name.startswith("final"):
            assert discovery_content.discovery in data
            assert discovery_content.pandas_general_description in data
            assert str(discovery_content.pandas_categorical_description) in data
            assert str(discovery_content.pandas_numerical_description) in data
        else:
            assert "final discovery" in data


def test_write_txt_final(
    discovery_with_discovery_content: Discovery, discovery_content: DiscoveryContent
) -> None:
    discovery_with_discovery_content.to_txt(file_name="final")

    with open("final_discovery.txt") as f:
        data = f.read()

    os.remove("final_discovery.txt")

    assert "final discovery" in data


def test_write_markdown_final(
    discovery_with_discovery_content: Discovery, discovery_content: DiscoveryContent
) -> None:
    discovery_with_discovery_content.to_markdown(file_name="final")

    with open("final_discovery.md") as f:
        data = f.read()

    os.remove("final_discovery.md")

    assert "final discovery" in data


def test_write_txt_file(
    discovery_with_discovery_content: Discovery, discovery_content: DiscoveryContent
) -> None:
    discovery_with_discovery_content.to_txt(file_name="a.csv")

    with open("a_discovery.txt") as f:
        data = f.read()

    os.remove("a_discovery.txt")

    assert discovery_content.discovery in data
    assert discovery_content.pandas_general_description in data
    assert str(discovery_content.pandas_categorical_description) in data
    assert str(discovery_content.pandas_numerical_description) in data


def test_write_markdown_file(
    discovery_with_discovery_content: Discovery, discovery_content: DiscoveryContent
) -> None:
    discovery_with_discovery_content.to_markdown(file_name="a.csv")

    with open("a_discovery.md") as f:
        data = f.read()

    os.remove("a_discovery.md")

    assert discovery_content.discovery in data
    assert discovery_content.pandas_general_description in data
    assert str(discovery_content.pandas_categorical_description) in data
    assert str(discovery_content.pandas_numerical_description) in data


def test_write_txt_raise_error_no_file(
    discovery_with_discovery_content: Discovery,
) -> None:
    with pytest.raises(ValueError):
        discovery_with_discovery_content.to_txt(file_name="bad.csv")


def test_write_markdown_raise_error_no_file(
    discovery_with_discovery_content: Discovery,
) -> None:
    with pytest.raises(ValueError):
        discovery_with_discovery_content.to_markdown(file_name="bad.csv")
