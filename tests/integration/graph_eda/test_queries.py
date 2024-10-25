import neo4j
import pandas as pd

from neo4j_runway import PyIngest
from neo4j_runway.database.neo4j import Neo4jGraph
from neo4j_runway.graph_eda import queries
from tests.resources.answers.people_pets import people_pets_yaml_string

data = pd.read_csv("tests/resources/data/people-pets.csv")
# convert to lists
data["knows"] = data["knows"].apply(lambda x: x[1:-1].split(", "))
# explode lists for data loading
data = data.explode("knows")

# clear database before loading
with neo4j.GraphDatabase.driver(
    uri="bolt://localhost:7687", auth=("neo4j", "password")
).session() as session:
    session.run(
        """
                match (n)-[r]-()
                detach delete n, r
                ;
                """
    )
    session.run(
        """
                match (n)
                delete n
                ;
                """
    )
    session.run(
        """
                CALL apoc.schema.assert({}, {})
                ;
                """
    )
    session.run("merge (n:Test {id:'1'}) SET n:Label2")

PyIngest(config=people_pets_yaml_string, dataframe=data)


def test_get_database_indexes(neo4j_graph: Neo4jGraph) -> None:
    result = queries.get_database_indexes(
        driver=neo4j_graph.driver, database=neo4j_graph.database
    )

    assert len(result) == 4


def test_get_database_contraints(neo4j_graph: Neo4jGraph) -> None:
    result = queries.get_database_constraints(
        driver=neo4j_graph.driver, database=neo4j_graph.database
    )

    assert len(result) == 2


def test_get_disconnected_node_count(neo4j_graph: Neo4jGraph) -> None:
    result = queries.get_disconnected_node_count(
        driver=neo4j_graph.driver, database=neo4j_graph.database
    )

    assert result == 1


def test_get_disconnected_node_count_by_label(neo4j_graph: Neo4jGraph) -> None:
    result = queries.get_disconnected_node_count_by_label(
        driver=neo4j_graph.driver, database=neo4j_graph.database
    )

    assert len(result) == 1


def test_get_disconnected_node_ids(neo4j_graph: Neo4jGraph) -> None:
    result = queries.get_disconnected_node_ids(
        driver=neo4j_graph.driver, database=neo4j_graph.database
    )

    assert len(result) == 1


def test_get_multi_label_node_counts(neo4j_graph: Neo4jGraph) -> None:
    result = queries.get_node_multi_label_counts(
        driver=neo4j_graph.driver, database=neo4j_graph.database
    )

    assert len(result) == 1


def test_get_node_count(neo4j_graph: Neo4jGraph) -> None:
    result = queries.get_node_count(
        driver=neo4j_graph.driver, database=neo4j_graph.database
    )

    assert result == 20


def test_get_node_degrees(neo4j_graph: Neo4jGraph) -> None:
    result = queries.get_node_degrees(
        driver=neo4j_graph.driver, database=neo4j_graph.database
    )

    assert len(result) == 20


def test_get_node_label_counts(neo4j_graph: Neo4jGraph) -> None:
    result = queries.get_node_label_counts(
        driver=neo4j_graph.driver, database=neo4j_graph.database
    )

    assert len(result) == 5


def test_get_node_properties(neo4j_graph: Neo4jGraph) -> None:
    result = queries.get_node_properties(
        driver=neo4j_graph.driver, database=neo4j_graph.database
    )

    assert len(result) == 9


def test_get_relationship_count(neo4j_graph: Neo4jGraph) -> None:
    result = queries.get_relationship_count(
        driver=neo4j_graph.driver, database=neo4j_graph.database
    )

    assert result == 24


def test_get_relationship_properties(neo4j_graph: Neo4jGraph) -> None:
    result = queries.get_relationship_properties(
        driver=neo4j_graph.driver, database=neo4j_graph.database
    )

    assert len(result) == 0


def test_get_relationship_type_counts(neo4j_graph: Neo4jGraph) -> None:
    result = queries.get_relationship_type_counts(
        driver=neo4j_graph.driver, database=neo4j_graph.database
    )

    assert len(result) == 4


def test_get_unlabeled_node_count(neo4j_graph: Neo4jGraph) -> None:
    result = queries.get_unlabeled_node_count(
        driver=neo4j_graph.driver, database=neo4j_graph.database
    )

    assert result == 0


def test_get_unlabeled_node_ids(neo4j_graph: Neo4jGraph) -> None:
    result = queries.get_unlabeled_node_ids(
        driver=neo4j_graph.driver, database=neo4j_graph.database
    )

    assert len(result) == 0
