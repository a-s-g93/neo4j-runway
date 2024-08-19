from unittest.mock import MagicMock, patch

import pytest

from neo4j_runway.modeler import GraphDataModeler

data_dictionary = {
    "a.csv": {"a": "test", "b": "test2"},
    "b.csv": {"c": "test3"},
}


@patch(
    "neo4j_runway.llm.openai.data_modeling.OpenAIDataModelingLLM._get_data_model_response"
)
def test_create_initial_model(
    mock_llm: MagicMock,
    mock_discovery: MagicMock,
    mock_user_input: MagicMock,
    mock_data_model: MagicMock,
) -> None:
    with pytest.warns(UserWarning):
        gdm = GraphDataModeler(llm=mock_llm, data_dictionary=data_dictionary)

    gdm.create_initial_model()
    assert len(gdm.model_history) == 1
    assert mock_llm.return_value._get_data_model_response.assert_called_once


def test_iterate_model(
    mock_llm: MagicMock,
    mock_discovery: MagicMock,
    mock_user_input: MagicMock,
    mock_data_model: MagicMock,
) -> None:
    with pytest.warns(UserWarning):
        gdm = GraphDataModeler(llm=mock_llm, data_dictionary=data_dictionary)

    gdm._initial_model_created = True
    gdm.model_history = [mock_data_model]

    assert len(gdm.model_history) == 1

    gdm.iterate_model()

    assert mock_llm.return_value._get_data_model_response.assert_called_once
