import os

import neo4j
import pandas as pd
import pytest

from neo4j_runway import PyIngest
from neo4j_runway.database.neo4j import Neo4jGraph
from tests.resources.answers.people_pets import people_pets_yaml_string


@pytest.fixture(autouse=True, scope="module")
def setup_graph():
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


@pytest.fixture(scope="module")
def neo4j_graph() -> Neo4jGraph:
    return Neo4jGraph(
        **{
            "username": os.environ.get("NEO4J_USERNAME"),
            "password": os.environ.get("NEO4J_PASSWORD"),
            "uri": os.environ.get("NEO4J_URI"),
            "database": os.environ.get("NEO4J_DATABASE"),
        }
    )


@pytest.fixture(scope="module")
def refresh_database() -> None:
    with neo4j.GraphDatabase.driver(
        uri="bolt://localhost:7687", auth=("neo4j", "password")
    ).session() as session:
        session.run("match (n)-[r]-() detach delete n, r")
        session.run("""
CALL apoc.schema.assert({},{},true) YIELD label, key
RETURN *
""")

    PyIngest(config=people_pets_yaml_string.replace("file:./", "file:./tests"))
