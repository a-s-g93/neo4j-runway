import os
import unittest

from dotenv import load_dotenv
from neo4j import GraphDatabase

from neo4j_runway.ingestion.pyingest import PyIngest
from tests.resources.answers.people_pets import people_pets_multi_csv_yaml_string

load_dotenv()

username = os.environ.get("NEO4J_USERNAME")
password = os.environ.get("NEO4J_PASSWORD")
uri = os.environ.get("NEO4J_URI")
database = os.environ.get("NEO4J_DATABASE")


class TestPyIngestLoadMultiCSV(unittest.TestCase):
    """
    Requires .env file in tests/ containing NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE.
    Use a unique test database as contents will be deleted each run.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.driver = GraphDatabase.driver(
            uri=uri,
            auth=(username, password),
        )

        # clear database before loading
        with cls.driver.session(database=database) as session:
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

        PyIngest(config=people_pets_multi_csv_yaml_string)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.driver.close()

    def test_person_node_count(self) -> None:
        person_cypher = "match (p:Person) return count(p)"
        with self.driver.session(database=database) as session:
            r = session.run(person_cypher).single().value()
            self.assertEqual(5, r)

    def test_pet_node_count(self) -> None:
        pet_cypher = "match (p:Pet) return count(p)"
        with self.driver.session(database=database) as session:
            r = session.run(pet_cypher).single().value()
            self.assertEqual(5, r)

    def test_toy_node_count(self) -> None:
        toy_cypher = "match (p:Toy) return count(p)"
        with self.driver.session(database=database) as session:
            r = session.run(toy_cypher).single().value()
            self.assertEqual(5, r)

    def test_address_node_count(self) -> None:
        address_cypher = "match (p:Address) return count(p)"
        with self.driver.session(database=database) as session:
            r = session.run(address_cypher).single().value()
            self.assertEqual(4, r)

    def test_shelter_node_count(self) -> None:
        address_cypher = "match (p:Shelter) return count(p)"
        with self.driver.session(database=database) as session:
            r = session.run(address_cypher).single().value()
            self.assertEqual(2, r)

    def test_person_to_pet_relationship_counts(self) -> None:
        cypher = "match (:Person)-[r:HAS_PET]-(:Pet) return count(r)"
        with self.driver.session(database=database) as session:
            r = session.run(cypher).single().value()
            self.assertEqual(5, r)

    def test_person_to_address_relationship_counts(self) -> None:
        cypher = "match (:Person)-[r:HAS_ADDRESS]-(:Address) return count(r)"
        with self.driver.session(database=database) as session:
            r = session.run(cypher).single().value()
            self.assertEqual(5, r)

    def test_pet_to_toy_relationship_counts(self) -> None:
        cypher = "match (:Pet)-[r:PLAYS_WITH]-(:Toy) return count(r)"
        with self.driver.session(database=database) as session:
            r = session.run(cypher).single().value()
            self.assertEqual(5, r)

    def test_pet_to_shelter_relationship_counts(self) -> None:
        cypher = "match (:Pet)-[r:FROM_SHELTER]-(:Shelter) return count(r)"
        with self.driver.session(database=database) as session:
            r = session.run(cypher).single().value()
            self.assertEqual(5, r)

    def test_person_to_person_relationship_counts(self) -> None:
        cypher = "match (:Person)-[r:KNOWS]->(:Person) return count(r)"
        with self.driver.session(database=database) as session:
            r = session.run(cypher).single().value()
            self.assertEqual(9, r)

    def test_constraints_present(self) -> None:
        cypher = "show constraints yield name return name"
        with self.driver.session(database=database) as session:
            r = set(session.run(cypher).value())
            self.assertEqual(
                {
                    "person_name",
                    "toy_name",
                    "address_city_street",
                    "pet_name",
                    "shelter_name",
                },
                r,
            )


if __name__ == "__main__":
    unittest.main()
