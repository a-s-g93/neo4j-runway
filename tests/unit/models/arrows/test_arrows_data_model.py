import os
import unittest
from ast import literal_eval

from neo4j_runway.models import (
    ArrowsDataModel,
    DataModel,
    Node,
    Property,
    Relationship,
)


class TestDataModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.columns = [
            "name",
            "age",
            "street",
            "city",
            "pet_name",
            "pet",
            "toy",
            "toy_type",
        ]

        person_name = Property(
            name="name", type="str", csv_mapping="name", is_unique=True
        )
        person_age = Property(
            name="age", type="int", csv_mapping="age", is_unique=False
        )
        address_street = Property(
            name="street", type="str", csv_mapping="street", is_unique=False
        )
        address_city = Property(
            name="city", type="str", csv_mapping="city", is_unique=False
        )
        pet_name = Property(
            name="name", type="str", csv_mapping="pet_name", is_unique=False
        )
        pet_kind = Property(name="kind", type="str", csv_mapping="pet", is_unique=False)
        toy_name = Property(name="name", type="str", csv_mapping="toy", is_unique=True)
        toy_kind = Property(
            name="kind", type="str", csv_mapping="toy_type", is_unique=False
        )

        cls.good_nodes = [
            Node(
                label="Person",
                properties=[person_name, person_age],
            ),
            Node(
                label="Address",
                properties=[address_street, address_city],
            ),
            Node(
                label="Pet",
                properties=[pet_name, pet_kind],
            ),
            Node(
                label="Toy",
                properties=[toy_name, toy_kind],
            ),
        ]

        cls.good_relationships = [
            Relationship(
                type="HAS_ADDRESS",
                properties=[],
                source="Person",
                target="Address",
            ),
            Relationship(
                type="KNOWS",
                properties=[],
                source="Person",
                target="Person",
            ),
            Relationship(
                type="HAS_PET",
                properties=[],
                source="Person",
                target="Pet",
            ),
            Relationship(
                type="PLAYS_WITH",
                properties=[],
                source="Pet",
                target="Toy",
            ),
        ]

        cls.data_model = DataModel(
            nodes=cls.good_nodes, relationships=cls.good_relationships
        )

    def test_arrows_init(self) -> None:
        """
        Test init.
        """
        self.data_model.to_arrows(write_file=False)

    def test_json_generation(self) -> None:
        """
        Test the JSON generation for import into arrows.app.
        """

        file_path = "test-arrows-output.json"
        self.data_model.to_arrows(file_path=file_path, write_file=True)

        with open(f"./{file_path}", "r") as f:
            content = literal_eval(f.read())
            ArrowsDataModel(
                nodes=content["nodes"], relationships=content["relationships"]
            )

        try:
            os.remove(f"./{file_path}")
        except Exception:
            print("No arrows data model created.")


if __name__ == "__main__":
    unittest.main()
