import json
import os
import unittest

from neo4j_runway.models import (
    DataModel,
    Node,
    Property,
    Relationship,
)


class TestSolutionsWorkbenchDataModel(unittest.TestCase):
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
            name="name",
            csv_mapping_other="knows",
            type="str",
            csv_mapping="name",
            is_unique=True,
        )
        person_age = Property(
            name="age", type="int", csv_mapping="age", is_unique=False
        )
        address_street = Property(
            name="street",
            type="str",
            csv_mapping="street",
            is_unique=True,
            part_of_key=True,
        )
        address_city = Property(
            name="city",
            type="str",
            csv_mapping="city",
            is_unique=True,
            part_of_key=True,
        )
        pet_name = Property(
            name="name", type="str", csv_mapping="pet_name", is_unique=True
        )
        pet_kind = Property(name="kind", type="str", csv_mapping="pet", is_unique=False)
        toy_name = Property(name="name", type="str", csv_mapping="toy", is_unique=True)
        toy_kind = Property(
            name="kind", type="str", csv_mapping="toy_type", is_unique=False
        )
        shelter_name = Property(
            name="name", csv_mapping="shelter_name", type="str", is_unique=True
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
            Node(label="Shelter", properties=[shelter_name]),
        ]

        cls.good_relationships = [
            Relationship(
                type="HAS_ADDRESS",
                properties=[],
                source="Person",
                target="Address",
            ),
            Relationship(
                type="HAS_ADDRESS",
                properties=[],
                source="Shelter",
                target="Address",
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
            Relationship(
                type="FROM_SHELTER",
                properties=[],
                source="Pet",
                target="Shelter",
            ),
            Relationship(
                type="KNOWS",
                properties=[],
                source="Person",
                target="Person",
            ),
        ]

        cls.data_model = DataModel(
            nodes=cls.good_nodes, relationships=cls.good_relationships
        )

    def test_core_to_solutions_workbench_data_model(self) -> None:
        """
        Test init to SW data model.
        """
        swdm = self.data_model.to_solutions_workbench(write_file=False)

        self.assertEqual(len(swdm.nodeLabels), 5)
        self.assertEqual(len(swdm.relationshipTypes), 6)

    def test_solutions_workbench_to_core_data_model(self) -> None:
        """
        Test init from SW data model.
        """

        dm = DataModel.from_solutions_workbench(
            file_path="tests/resources/data_models/pets-solutions-workbench.json"
        )

        self.assertEqual(len(dm.nodes), 5)
        self.assertEqual(len(dm.relationships), 6)
        self.assertIsNotNone(dm.metadata)

        dm.to_solutions_workbench(
            file_path="converted-data-model-sw-test.json", write_file=False
        )

    def test_json_output(self) -> None:
        """
        Test the JSON generation for import into Solutions Workbench.
        """

        file_path = "test-solutions-workbench-output.json"
        self.data_model.to_solutions_workbench(file_path=file_path, write_file=True)

        with open(f"./{file_path}", "r") as f:
            content = json.loads(f.read())

            self.assertEqual(set(content.keys()), {"dataModel", "metadata"})
            self.assertEqual(len(content["dataModel"]["nodeLabels"].keys()), 5)
            self.assertEqual(len(content["dataModel"]["relationshipTypes"].keys()), 6)

        try:
            os.remove(f"./{file_path}")
        except Exception:
            print("No Solutions Workbench data model created.")


if __name__ == "__main__":
    unittest.main()
