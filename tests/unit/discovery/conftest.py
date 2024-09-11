from unittest.mock import MagicMock

import pytest

from neo4j_runway.llm.openai.discovery import OpenAIDiscoveryLLM


@pytest.fixture
def mock_create_discovery_prompt_multi_file(mocker):
    return mocker.patch(
        "neo4j_runway.discovery.discovery.create_discovery_prompt_multi_file",
        return_value="mock prompt",
    )


@pytest.fixture(scope="function")
def mock_llm() -> MagicMock:
    m = MagicMock(spec=OpenAIDiscoveryLLM)
    m.is_async = False

    return m


@pytest.fixture(scope="function")
def mock_async_llm() -> MagicMock:
    m = MagicMock(spec=OpenAIDiscoveryLLM)
    m.is_async = True

    return m
