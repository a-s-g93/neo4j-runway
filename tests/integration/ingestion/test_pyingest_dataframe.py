import os
import unittest

import pandas as pd
from dotenv import load_dotenv
from neo4j import GraphDatabase

from neo4j_runway.ingestion.pyingest import PyIngest
from tests.resources.answers.people_pets import people_pets_yaml_string

load_dotenv()


class TestPyIngestLoadDataFrame(unittest.TestCase):
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
        data = pd.read_csv("tests/resources/data/people-pets.csv")
        # convert to lists
        data["knows"] = data["knows"].apply(lambda x: x[1:-1].split(", "))
        # explode lists for data loading
        cls.data = data.explode("knows")

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
        PyIngest(config=people_pets_yaml_string, dataframe=cls.data)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.driver.close()

    def test_person_node_count(self) -> None:
        person = self.data["name"].nunique()
        person_cypher = "match (p:Person) return count(p)"
        with self.driver.session(database=os.environ.get("NEO4J_DATABASE")) as session:
            r = session.run(person_cypher).single().value()
            self.assertEqual(person, r)

    def test_pet_node_count(self) -> None:
        pet = self.data["pet_name"].nunique()
        pet_cypher = "match (p:Pet) return count(p)"
        with self.driver.session(database=os.environ.get("NEO4J_DATABASE")) as session:
            r = session.run(pet_cypher).single().value()
            self.assertEqual(pet, r)

    def test_toy_node_count(self) -> None:
        toy = self.data["toy"].nunique()
        toy_cypher = "match (p:Toy) return count(p)"
        with self.driver.session(database=os.environ.get("NEO4J_DATABASE")) as session:
            r = session.run(toy_cypher).single().value()
            self.assertEqual(toy, r)

    def test_address_node_count(self) -> None:
        address = len(set(self.data["city"] + self.data["street"]))
        address_cypher = "match (p:Address) return count(p)"
        with self.driver.session(database=os.environ.get("NEO4J_DATABASE")) as session:
            r = session.run(address_cypher).single().value()
            self.assertEqual(address, r)

    def test_person_to_person_relationship_counts(self) -> None:
        person_to_person = len(self.data)
        cypher = """
        unwind $names as name
        match (:Person {name: name})-[r:KNOWS]->(:Person) return count(r)
        """
        with self.driver.session(database=os.environ.get("NEO4J_DATABASE")) as session:
            r = (
                session.run(
                    cypher, parameters={"names": list(self.data["name"].unique())}
                )
                .single()
                .value()
            )
            self.assertEqual(person_to_person, r)

    def test_person_to_pet_relationship_counts(self) -> None:
        person_to_pet = self.data["pet_name"].nunique()  # all pets have 1 owner
        cypher = "match (:Person)-[r:HAS_PET]-(:Pet) return count(r)"
        with self.driver.session(database=os.environ.get("NEO4J_DATABASE")) as session:
            r = session.run(cypher).single().value()
            self.assertEqual(person_to_pet, r)

    def test_person_to_address_relationship_counts(self) -> None:
        person_to_address = self.data["name"].nunique()  # all people have 1 address
        cypher = "match (:Person)-[r:HAS_ADDRESS]-(:Address) return count(r)"
        with self.driver.session(database=os.environ.get("NEO4J_DATABASE")) as session:
            r = session.run(cypher).single().value()
            self.assertEqual(person_to_address, r)

    def test_pet_to_toy_relationship_counts(self) -> None:
        pet_to_toy = self.data["toy"].nunique()
        cypher = "match (:Pet)-[r:PLAYS_WITH]-(:Toy) return count(r)"
        with self.driver.session(database=os.environ.get("NEO4J_DATABASE")) as session:
            r = session.run(cypher).single().value()
            self.assertEqual(pet_to_toy, r)

    def test_constraints_present(self) -> None:
        cypher = "show constraints yield name return name"
        with self.driver.session(database=os.environ.get("NEO4J_DATABASE")) as session:
            r = set(session.run(cypher).value())
            self.assertEqual({"person_name", "toy_name"}, r)


if __name__ == "__main__":
    unittest.main()
