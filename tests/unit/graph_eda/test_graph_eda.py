from unittest.mock import MagicMock, patch

from neo4j_runway.graph_eda import GraphEDA


@patch.object(GraphEDA, "_process_request", spec=GraphEDA._process_request)
def test_database_constraints(
    mock_graph_eda: MagicMock, mock_neo4j_graph: MagicMock
) -> None:
    eda = GraphEDA(mock_neo4j_graph)
    eda._process_request.return_value = [{"test": "value"}]

    assert eda.database_constraints() == [{"test": "value"}]


@patch.object(GraphEDA, "_process_request", spec=GraphEDA._process_request)
def test_run_include(mock_graph_eda: MagicMock, mock_neo4j_graph: MagicMock) -> None:
    eda = GraphEDA(mock_neo4j_graph)
    eda._process_request.return_value = [{"test": "value"}]

    eda.run(include=["database_constraints"])

    assert eda._process_request.call_count == 1


@patch.object(GraphEDA, "_process_request", spec=GraphEDA._process_request)
def test_run_exclude(mock_graph_eda: MagicMock, mock_neo4j_graph: MagicMock) -> None:
    eda = GraphEDA(mock_neo4j_graph)
    eda._process_request.return_value = [{"test": "value"}]

    num_methods = len(eda.available_methods)

    eda.run(
        exclude=[
            "node_count",
            "relationship_count",
            "unlabeled_node_count",
            "disconnected_node_count",
        ]
    )

    assert eda._process_request.call_count == num_methods - 4


@patch.object(GraphEDA, "_process_request", spec=GraphEDA._process_request)
def test_run_include_and_exclude(
    mock_graph_eda: MagicMock, mock_neo4j_graph: MagicMock
) -> None:
    eda = GraphEDA(mock_neo4j_graph)
    eda._process_request.return_value = [{"test": "value"}]

    eda.run(
        include=["database_constraints"],
        exclude=[
            "node_count",
            "relationship_count",
            "unlabeled_node_count",
            "disconnected_node_count",
        ],
    )

    assert eda._process_request.call_count == 1


@patch.object(GraphEDA, "node_degrees")
def test_run_with_method_params(
    mock_graph_eda: MagicMock, mock_neo4j_graph: MagicMock
) -> None:
    eda = GraphEDA(mock_neo4j_graph)
    params = {"node_degrees": {"order_by": "in", "top_k": 7}}

    eda.run(refresh=True, include=["node_degrees"], method_params=params)

    assert eda.node_degrees.call_count == 1
    eda.node_degrees.assert_called_with(order_by="in", top_k=7, refresh=True)
