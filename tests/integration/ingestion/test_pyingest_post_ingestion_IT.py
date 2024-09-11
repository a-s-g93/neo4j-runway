import os
import unittest

from dotenv import load_dotenv
from neo4j import GraphDatabase

from neo4j_runway.ingestion.pyingest import PyIngest

load_dotenv()

# These credentials are for the dummy data testing only. Do NOT use the same credentials here for production graphs.
username = os.environ.get("NEO4J_USERNAME")
password = os.environ.get("NEO4J_PASSWORD")
uri = os.environ.get("NEO4J_URI")
database = os.environ.get("NEO4J_DATABASE")


class TestPyIngestPostIngestion(unittest.TestCase):
    """
    Requires .env file in tests/ containing NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE.
    Use a unique test database as contents will be deleted each run.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.driver = GraphDatabase.driver(
            uri=os.environ.get("NEO4J_URI"),
            auth=(os.environ.get("NEO4J_USERNAME"), os.environ.get("NEO4J_PASSWORD")),
        )

        # clear database before loading
        with cls.driver.session(database=os.environ.get("NEO4J_DATABASE")) as session:
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

        PyIngest(config="tests/resources/configs/post-ingest.yml")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.driver.close()

    def test_test_node_present(self) -> None:
        cypher = "match (t:Test) return count(t)"
        with self.driver.session(database=database) as session:
            r = session.run(cypher).single().value()
            self.assertEqual(1, r)

    def test_test_node2_present(self) -> None:
        cypher = "match (t:Test2) return t.var as var"
        with self.driver.session(database=database) as session:
            r = session.run(cypher).single().value()
            self.assertEqual(2, r)


if __name__ == "__main__":
    unittest.main()
