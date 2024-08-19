from unittest.mock import MagicMock

import pytest

from neo4j_runway.discovery import Discovery
from neo4j_runway.inputs import UserInput
from neo4j_runway.llm.openai.data_modeling import OpenAIDataModelingLLM
from neo4j_runway.models.core import DataModel


@pytest.fixture(scope="function")
def mock_llm() -> MagicMock:
    m = MagicMock(spec=OpenAIDataModelingLLM)

    m._get_initial_data_model_response.return_value = mock_data_model
    m._get_data_model_response.return_value = mock_data_model
    return m


@pytest.fixture(scope="function")
def mock_discovery() -> MagicMock:
    return MagicMock(spec=Discovery)


@pytest.fixture(scope="function")
def mock_user_input() -> MagicMock:
    return MagicMock(spec=UserInput)


@pytest.fixture(scope="function")
def mock_data_model() -> MagicMock:
    return MagicMock(spec=DataModel)
