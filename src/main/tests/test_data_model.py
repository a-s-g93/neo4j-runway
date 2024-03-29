import unittest
# import os

from objects.node import Node
from objects.relationship import Relationship
from objects.property import Property
from objects.data_model import DataModel


class TestDataModel(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.columns = ["name", "age", "street", "city", "pet_name", "pet", "toy", "toy_type"]

        person_name = Property(name="name", type="str", csv_mapping="name", is_unique=True)
        person_age = Property(name="age", type="str", csv_mapping="age", is_unique=False)
        address_street = Property(name="street", type="str", csv_mapping="street", is_unique=False)
        address_city = Property(name="city", type="str", csv_mapping="city", is_unique=False)
        pet_name = Property(name="name", type="str", csv_mapping="pet_name", is_unique=False)
        pet_kind = Property(name="kind", type="str", csv_mapping="pet", is_unique=False)
        toy_name = Property(name="name", type="str", csv_mapping="toy", is_unique=True)
        toy_kind = Property(name="kind", type="str", csv_mapping="toy_type", is_unique=False)

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
            )
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
                    )
                ]
        cls.bad_relationships = cls.good_relationships+[
            Relationship(
                        type="BAD",
                        properties=[],
                        source="Dog",
                        target="Toy",
                    )
        ]
        cls.bad_nodes = cls.good_nodes + [
            Node(
                label="Toy", 
                properties=[toy_name, toy_kind], 
            )
        ]

    def test_bad_init(self) -> None:
        """
        Test bad input for init.
        """

        test_model = DataModel(
                nodes=self.bad_nodes, relationships=self.bad_relationships
            )
        validation = test_model.validate_model(csv_columns=self.columns)
        self.assertFalse(validation['valid'])
        self.assertIn("BAD", validation['message'].split())
        self.assertIn("Dog", validation['message'].split())
        self.assertIn("source", validation['message'].split())


    def test_good_init(self) -> None:
        """
        This input should pass.
        """

        # valid
        self.assertIsInstance(DataModel(nodes=self.good_nodes, relationships=self.good_relationships), DataModel)
    
    def test_to_dict(self) -> None:
        """
        Test dict property.
        """

        test_model = DataModel(nodes=self.good_nodes, relationships=self.good_relationships)

        test_dict = test_model.model_dump()

        self.assertEqual(list(test_dict.keys()), ["nodes", "relationships"])
        self.assertEqual(list(test_dict['nodes'][0].keys()), ['label', 'properties'])
        self.assertEqual(list(test_dict['relationships'][0].keys()), ['type', 'properties', 'source', 'target'])

if __name__ == "__main__":
    unittest.main()
