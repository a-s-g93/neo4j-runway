import os
import unittest
from ast import literal_eval

from neo4j_runway.models import (
    DataModel,
    Node,
    Property,
    Relationship,
)
from neo4j_runway.models.arrows import ArrowsDataModel


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
            "knows",
        ]

        person_name = Property(
            name="name",
            type="str",
            column_mapping="name",
            is_unique=True,
            alias="knows",
        )
        person_age = Property(
            name="age", type="int", column_mapping="age", is_unique=False
        )
        address_street = Property(
            name="street",
            type="str",
            column_mapping="street",
            is_unique=False,
            part_of_key=True,
        )
        address_city = Property(
            name="city",
            type="str",
            column_mapping="city",
            is_unique=False,
            part_of_key=True,
        )
        pet_name = Property(
            name="name", type="str", column_mapping="pet_name", is_unique=True
        )
        pet_kind = Property(
            name="kind", type="str", column_mapping="pet", is_unique=False
        )
        toy_name = Property(
            name="name", type="str", column_mapping="toy", is_unique=True
        )
        toy_kind = Property(
            name="kind", type="str", column_mapping="toy_type", is_unique=False
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
                source="Person",
                target="Address",
            ),
            Relationship(
                type="KNOWS",
                source="Person",
                target="Person",
            ),
            Relationship(
                type="HAS_PET",
                source="Person",
                target="Pet",
            ),
            Relationship(
                type="PLAYS_WITH",
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
