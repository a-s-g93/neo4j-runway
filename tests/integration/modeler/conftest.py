from unittest.mock import MagicMock

import pytest

from neo4j_runway.discovery.discovery import Discovery
from neo4j_runway.inputs import UserInput
from neo4j_runway.llm.openai import OpenAIDataModelingLLM
from neo4j_runway.modeler import GraphDataModeler
from neo4j_runway.models import DataModel
from neo4j_runway.utils.data.data_dictionary.data_dictionary import DataDictionary
from neo4j_runway.utils.data.table_collection import TableCollection
from neo4j_runway.warnings import ExperimentalFeatureWarning


@pytest.fixture(scope="function")
def mock_discovery(mock_data_dictionary: MagicMock) -> MagicMock:
    m = MagicMock(spec=Discovery)
    m.discovery = "Fake Discovery"
    m.data = MagicMock(spec=TableCollection)
    m.data.data_dictionary = mock_data_dictionary
    return m


@pytest.fixture(scope="function")
def mock_data_model() -> MagicMock:
    m = MagicMock(spec=DataModel)
    return m


# data_model = DataModel(
#     nodes=data_model_dict["nodes"],
#     relationships=data_model_dict["relationships"],
# )


@pytest.fixture(scope="function")
def mock_data_dictionary() -> MagicMock:
    m = MagicMock(spec=DataDictionary)
    return m


@pytest.fixture(scope="function")
def mock_llm() -> MagicMock:
    return MagicMock(spec=OpenAIDataModelingLLM)


@pytest.fixture(scope="function")
def graph_data_modeler_with_data_model(
    mock_llm: MagicMock, mock_data_model: MagicMock, mock_discovery: MagicMock
) -> MagicMock:
    with pytest.warns(ExperimentalFeatureWarning):
        gdm = GraphDataModeler(llm=mock_llm, discovery=mock_discovery)
        gdm._initial_model_created = True
        gdm.model_history = [mock_data_model]
        return gdm
