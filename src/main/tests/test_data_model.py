import unittest
# import os

from objects.node import Node
from objects.relationship import Relationship
from objects.data_model import DataModel


class TestValidation(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.columns = ["name", "age", "street", "city"]

        cls.bad_nodes = [
            Node(
                label="Person",
                properties=["name", "age"],
                unique_constraints=["lastName"],
                ),
            Node(
                label="Address", 
                properties=["street", "state"], 
                unique_constraints=None
            )
        ]

        cls.bad_relationships = [
            Relationship(
                type="HAS_ADDRESS",
                properties=["town"],
                unique_constraints=None,
                source="Person",
                target="Address",
            ),
            Relationship(
                type="KNOWS",
                unique_constraints=["score"],
                properties=None,
                source="Person",
                target="Person",
            ),
            Relationship(
                type="BAD",
                properties=None,
                source="City",
                target="Person",
            )
        ]

        cls.good_nodes = [
            Node(
                label="Person",
                properties=["name", "age"],
                unique_constraints=["name"],
                ),
            Node(
                label="Address", 
                properties=["street", "city"], 
                unique_constraints=None
            )
        ]

        cls.good_relationships = [
            Relationship(
                type="HAS_ADDRESS",
                properties=[],
                unique_constraints=None,
                source="Person",
                target="Address",
            ),
            Relationship(
                type="KNOWS",
                unique_constraints=[],
                properties=None,
                source="Person",
                target="Person",
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
        self.assertIn("City", validation['message'].split())
        self.assertIn("source", validation['message'].split())


    def test_good_init(self) -> None:
        """
        This input should pass.
        """

        self.assertEqual(Node(
                label="Person",
                properties=["name", "age"],
                unique_constraints=["name"],
            ).label,
            "Person"
        )

        self.assertEqual(Node(
                label="Person",
                properties=None,
                unique_constraints=None,
            ).label,
            "Person"
        )

        self.assertEqual(Relationship(type="HAS_ADDRESS",
                                       properties=None,
                                       unique_constraints=None,
                                       source="Person",
                                       target="Address").source,
                        "Person")
        
        # valid
        DataModel(nodes=self.good_nodes, relationships=self.good_relationships)
    
    def test_to_dict(self) -> None:
        """
        Test dict property.
        """

        test_model = DataModel(nodes=self.good_nodes, relationships=self.good_relationships)

        test_dict = test_model.dict

        self.assertEqual(list(test_dict.keys()), ["nodes", "relationships"])
        self.assertEqual(list(test_dict['nodes'][0].keys()), ['label', 'properties', 'unique_constraints'])
        self.assertEqual(list(test_dict['relationships'][0].keys()), ['type', 'properties', 'unique_constraints', 'source', 'target'])

    


if __name__ == "__main__":
    unittest.main()
