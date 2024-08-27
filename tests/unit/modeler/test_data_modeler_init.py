from unittest.mock import MagicMock

import pytest

from neo4j_runway.inputs import UserInput
from neo4j_runway.modeler import GraphDataModeler

data_dictionary = {
    "a.csv": {"a": "test", "b": "test2"},
    "b.csv": {"c": "test3"},
}

data_dictionary_alt = {
    "a.csv": {"a": "test"},
    "b.csv": {"c": "test3"},
}

allowed_columns = ["a", "b"]

use_cases = ["use case 1", "use case 2"]

user_input_data_dictionary = UserInput(data_dictionary=data_dictionary)

user_input_data_dictionary_alt = UserInput(data_dictionary=data_dictionary_alt)

user_input_full = UserInput(
    general_description="general", data_dictionary=data_dictionary, use_cases=use_cases
)

user_input_dict = {
    "general_description": "general dictionary",
    "a": "test",
    "b": "test2",
}


def test_init_data_dictionary_only(
    mock_llm: MagicMock, mock_discovery: MagicMock
) -> None:
    with pytest.warns():
        GraphDataModeler(llm=mock_llm, data_dictionary=data_dictionary)


def test_init_allowed_columns_only(
    mock_llm: MagicMock, mock_discovery: MagicMock
) -> None:
    with pytest.warns():
        GraphDataModeler(llm=mock_llm, allowed_columns=allowed_columns)


def test_init_user_input_dd_only(
    mock_llm: MagicMock, mock_discovery: MagicMock
) -> None:
    with pytest.warns():
        GraphDataModeler(llm=mock_llm, user_input=user_input_data_dictionary)


def test_init_user_input_full_only(
    mock_llm: MagicMock, mock_discovery: MagicMock
) -> None:
    with pytest.warns():
        GraphDataModeler(llm=mock_llm, user_input=user_input_full)


def test_init_user_input_dict_only(
    mock_llm: MagicMock, mock_discovery: MagicMock
) -> None:
    with pytest.warns():
        GraphDataModeler(llm=mock_llm, user_input=user_input_dict)


def test_init_dd_and_allowed_columns(
    mock_llm: MagicMock, mock_discovery: MagicMock
) -> None:
    with pytest.warns():
        GraphDataModeler(
            llm=mock_llm,
            data_dictionary=data_dictionary,
            allowed_columns=allowed_columns,
        )


def test_init_dd_and_user_input_dd(
    mock_llm: MagicMock, mock_discovery: MagicMock
) -> None:
    with pytest.warns():
        GraphDataModeler(
            llm=mock_llm,
            user_input=user_input_data_dictionary,
            data_dictionary=data_dictionary,
        )


def test_init_dd_and_user_input_dict(
    mock_llm: MagicMock, mock_discovery: MagicMock
) -> None:
    with pytest.warns():
        GraphDataModeler(
            llm=mock_llm, user_input=user_input_dict, data_dictionary=data_dictionary
        )


def test_init_allowed_columns_and_user_input_dd(
    mock_llm: MagicMock, mock_discovery: MagicMock
) -> None:
    with pytest.warns():
        GraphDataModeler(
            llm=mock_llm,
            user_input=user_input_data_dictionary,
            allowed_columns=allowed_columns,
        )


def test_init_allowed_columns_and_user_input_full(
    mock_llm: MagicMock, mock_discovery: MagicMock
) -> None:
    with pytest.warns():
        GraphDataModeler(
            llm=mock_llm, user_input=user_input_full, allowed_columns=allowed_columns
        )


def test_init_allowed_columns_and_user_input_dict(
    mock_llm: MagicMock, mock_discovery: MagicMock
) -> None:
    with pytest.warns():
        GraphDataModeler(
            llm=mock_llm, user_input=user_input_dict, allowed_columns=allowed_columns
        )
