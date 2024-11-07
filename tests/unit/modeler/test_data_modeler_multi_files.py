from unittest.mock import MagicMock

import pytest

from neo4j_runway.modeler import GraphDataModeler
from neo4j_runway.utils.data.data_dictionary.data_dictionary import DataDictionary
from neo4j_runway.warnings import ExperimentalFeatureWarning


def test_multifile_data_dictionary_init_allowed_columns(
    data_dictionary: DataDictionary,
) -> None:
    with pytest.warns(ExperimentalFeatureWarning):
        gdm = GraphDataModeler(
            llm="llm", discovery="disc", data_dictionary=data_dictionary
        )

    assert isinstance(gdm.allowed_columns, dict)
    assert gdm.allowed_columns["a.csv"] == ["a", "b"]
    assert gdm.allowed_columns["b.csv"] == ["c"]


def test_is_multifile_true(
    mock_llm: MagicMock, data_dictionary: DataDictionary
) -> None:
    with pytest.warns((UserWarning, ExperimentalFeatureWarning)):
        gdm = GraphDataModeler(llm=mock_llm, data_dictionary=data_dictionary)

    assert gdm.is_multifile


def test_is_multifile_false_no_named_file(
    mock_llm: MagicMock, data_dictionary_single_file: DataDictionary
) -> None:
    with pytest.warns(UserWarning):
        gdm = GraphDataModeler(
            llm=mock_llm, data_dictionary=data_dictionary_single_file
        )

    assert not gdm.is_multifile


def test_is_multifile_false_with_named_file(
    mock_llm: MagicMock, data_dictionary_single_file: DataDictionary
) -> None:
    with pytest.warns(UserWarning):
        gdm = GraphDataModeler(
            llm=mock_llm, data_dictionary=data_dictionary_single_file
        )

    assert not gdm.is_multifile


def test_allowed_columns(mock_llm: MagicMock, data_dictionary: DataDictionary) -> None:
    with pytest.warns((UserWarning, ExperimentalFeatureWarning)):
        gdm = GraphDataModeler(llm=mock_llm, data_dictionary=data_dictionary)

    assert "a.csv" in gdm.allowed_columns.keys()
    assert "b.csv" in gdm.allowed_columns.keys()
    assert "a" in gdm.allowed_columns.get("a.csv")
    assert "b" in gdm.allowed_columns.get("a.csv")
    assert "c" in gdm.allowed_columns.get("b.csv")
