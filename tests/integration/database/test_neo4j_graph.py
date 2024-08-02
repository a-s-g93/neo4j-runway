import os
import unittest

from neo4j_runway.database import Neo4jGraph


class TestNeo4jGraph(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.creds = {
            "username": os.environ.get("NEO4J_USERNAME"),
            "password": os.environ.get("NEO4J_PASSWORD"),
            "uri": os.environ.get("NEO4J_URI"),
            "database": os.environ.get("NEO4J_DATABASE"),
        }

    def test_init_with_provided_creds(self) -> None:
        g = Neo4jGraph(**self.creds)
        g.driver.close()

    def test_init_without_creds(self) -> None:
        g = Neo4jGraph()
        self.assertEqual("peoplepets", g.database)

        g.driver.close()

    def test_database_version_and_edition(self) -> None:
        g = Neo4jGraph(**self.creds)

        self.assertEqual("5.15.0", g.database_version)
        self.assertEqual("enterprise", g.database_edition)

        g.driver.close()

    def test_apoc_version(self) -> None:
        g = Neo4jGraph(**self.creds)

        self.assertEqual("5.15.1", g.apoc_version)

        g.driver.close()

    def test_schema(self) -> None:
        g = Neo4jGraph(**self.creds)

        self.assertIsNone(g._schema)

        self.assertIsInstance(g.schema, dict)

        self.assertIsInstance(g._schema, dict)

        g.driver.close()

    def test_verify(self) -> None:
        g = Neo4jGraph(**self.creds)
        res = g.verify()
        self.assertTrue(res["valid"])
        self.assertEqual(res["message"], "Connection and Auth Verified!")
