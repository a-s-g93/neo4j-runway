from unittest.mock import MagicMock

import pytest

from neo4j_runway.discovery import Discovery
from neo4j_runway.inputs import UserInput
from neo4j_runway.llm.openai.data_modeling import OpenAIDataModelingLLM
from neo4j_runway.models.core import DataModel
from neo4j_runway.utils.data.data_dictionary.column import Column
from neo4j_runway.utils.data.data_dictionary.data_dictionary import DataDictionary
from neo4j_runway.utils.data.data_dictionary.table_schema import TableSchema


@pytest.fixture(scope="function")
def mock_llm() -> MagicMock:
    m = MagicMock(spec=OpenAIDataModelingLLM)

    m._get_initial_data_model_response.return_value = mock_data_model
    m._get_data_model_response.return_value = mock_data_model
    return m


@pytest.fixture(scope="function")
def mock_discovery() -> MagicMock:
    d = MagicMock(spec=Discovery)
    d.user_input = mock_user_input
    return d


@pytest.fixture(scope="function")
def mock_user_input() -> MagicMock:
    return MagicMock(spec=UserInput)


@pytest.fixture(scope="function")
def mock_data_model() -> MagicMock:
    return MagicMock(spec=DataModel)


@pytest.fixture(scope="function")
def data_dictionary() -> DataDictionary:
    return DataDictionary(
        table_schemas=[
            TableSchema(
                name="a.csv",
                columns=[
                    Column(name="a", description="test"),
                    Column(name="b", description="test2"),
                ],
            ),
            TableSchema(
                name="b.csv",
                columns=[
                    Column(name="c", description="test3"),
                ],
            ),
        ]
    )


@pytest.fixture(scope="function")
def data_dictionary_single_file() -> DataDictionary:
    return DataDictionary(
        table_schemas=[
            TableSchema(
                name="a.csv",
                columns=[
                    Column(name="a", description="test"),
                    Column(name="b", description="test2"),
                ],
            )
        ]
    )


@pytest.fixture(scope="function")
def user_input_with_data_dictionary(data_dictionary: DataDictionary) -> UserInput:
    return UserInput(data_dictionary=data_dictionary)


@pytest.fixture(scope="function")
def user_input_full(data_dictionary: DataDictionary) -> UserInput:
    return UserInput(
        general_description="general",
        data_dictionary=data_dictionary,
        use_cases=["use case 1", "use case 2"],
    )
