import os
import unittest

from dotenv import load_dotenv
from neo4j import GraphDatabase

from neo4j_runway.code_generation import LoadCSVCodeGenerator
from neo4j_runway.models import DataModel

load_dotenv()

# These credentials are for the dummy data testing only. Do NOT use the same credentials here for production graphs.
username = os.environ.get("NEO4J_USERNAME")
password = os.environ.get("NEO4J_PASSWORD")
uri = os.environ.get("NEO4J_URI")
database = os.environ.get("NEO4J_DATABASE")


class TestLoadCSVViaAPIWithMultiCSV(unittest.TestCase):
    """
    Steps:
        1. Ensure local instance of Neo4j is available.
        2. Generate the LOAD CSV code with an imported data model from arrows.app.
        3. Load the data into a local instance of Neo4j. The csv is located at imports/ of the local instance.
        4. query local graph to ensure data loaded properly.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.driver = GraphDatabase.driver(
            uri=uri,
            auth=(username, password),
        )

        # clear all data in the database
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

        # contains node csv in caption or property
        # contains rel csv in property
        data_model = DataModel.from_arrows(
            "tests/resources/data_models/people-pets-arrows-multi-csv.json"
        )

        gen = LoadCSVCodeGenerator(data_model=data_model, csv_name="", method="api")

        load_csv_cypher = gen.generate_load_csv_cypher_string()

        # skip last "query" since it is an empty string
        for query in load_csv_cypher.split(";")[:-1]:
            with cls.driver.session(database=database) as session:
                session.run(query=query)

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
            self.assertEqual(3, r)

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

    def test_constraints_present(self) -> None:
        cypher = "show constraints yield name return name"
        with self.driver.session(database=database) as session:
            r = set(session.run(cypher).value())
            self.assertEqual(
                {
                    "person_name",
                    "toy_name",
                    "address_address",
                    "pet_name",
                    "shelter_name",
                },
                r,
            )


if __name__ == "__main__":
    unittest.main()
