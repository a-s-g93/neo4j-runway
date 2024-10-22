import os

import neo4j
import pytest

from neo4j_runway import PyIngest
from neo4j_runway.database.neo4j import Neo4jGraph
from tests.resources.answers.people_pets import people_pets_yaml_string


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

    # PyIngest(config="tests/resources/configs/people-pets.yml")
    PyIngest(config=people_pets_yaml_string.replace("file:./", "file:./tests"))
