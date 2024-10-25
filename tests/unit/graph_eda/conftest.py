from unittest.mock import MagicMock

import pytest

from neo4j_runway.database.neo4j import Neo4jGraph
from neo4j_runway.graph_eda import GraphEDA


@pytest.fixture(scope="function")
def mock_neo4j_graph() -> MagicMock:
    return MagicMock(spec=Neo4jGraph)


@pytest.fixture(scope="function")
def mock_graph_eda() -> MagicMock:
    return MagicMock(spec=GraphEDA)
