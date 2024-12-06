from unittest.mock import MagicMock, patch

import pytest

from neo4j_runway.modeler import GraphDataModeler
from neo4j_runway.utils.data.data_dictionary.data_dictionary import DataDictionary
from neo4j_runway.warnings import ExperimentalFeatureWarning


@patch(
    "neo4j_runway.llm.openai.data_modeling.OpenAIDataModelingLLM._get_data_model_response"
)
def test_create_initial_model(
    mock_llm: MagicMock, data_dictionary: DataDictionary
) -> None:
    with pytest.warns((UserWarning, ExperimentalFeatureWarning)):
        gdm = GraphDataModeler(llm=mock_llm, data_dictionary=data_dictionary)

    gdm.create_initial_model()
    assert len(gdm.model_history) == 1
    assert mock_llm.return_value._get_data_model_response.assert_called_once


def test_iterate_model(
    mock_llm: MagicMock, mock_data_model: MagicMock, data_dictionary: DataDictionary
) -> None:
    with pytest.warns((UserWarning, ExperimentalFeatureWarning)):
        gdm = GraphDataModeler(llm=mock_llm, data_dictionary=data_dictionary)

    gdm._initial_model_created = True
    gdm.model_history = [mock_data_model]

    assert len(gdm.model_history) == 1

    gdm.iterate_model()

    assert mock_llm.return_value._get_data_model_response.assert_called_once
