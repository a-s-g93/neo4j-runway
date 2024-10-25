from unittest.mock import MagicMock, patch

import pytest

from neo4j_runway.graph_eda import GraphEDA


@patch.object(GraphEDA, "_process_request", spec=GraphEDA._process_request)
def test_database_constraints(
    mock_graph_eda: MagicMock, mock_neo4j_graph: MagicMock
) -> None:
    eda = GraphEDA(mock_neo4j_graph)
    eda._process_request.return_value = [{"test": "value"}]

    assert eda.database_constraints() == [{"test": "value"}]
