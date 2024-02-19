import unittest
import os

from objects.node import Node
from objects.relationship import Relationship
from objects.data_model import DataModel


class TestValidation(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.columns = ["name", "age", "street", "city"]

    def test_bad_init(self) -> None:
        """
        Test bad input for init.
        """

        with self.assertRaises(Exception):
            Node(
                label="Person",
                properties=["name", "age"],
                unique_constraints=["lastName"],
            )

        # self.assertRaises(
        #     Exception,
        #     Node(
        #         label="Person",
        #         properties=["name", "age"],
        #         unique_constraints=["lastName"],
        #     ),
        # )

        # address_bad = Node(
        #     label="Address", properties=["street", "state"], unique_constraints=None
        # )
        # person_to_address_bad = Relationship(
        #     type="HAS_ADDRESS",
        #     properties=["town"],
        #     unique_constraints=None,
        #     source="Person",
        #     target="Address",
        # )
        # person_to_person_bad = Relationship(
        #     type="KNOWS",
        #     unique_constraints=["score"],
        #     properties=None,
        #     source="Person",
        #     target="Person",
        # )
        # test_data_model_invalid = DataModel(
        #     nodes=[person_bad, address_bad], relationships=[person_to_address_bad, person_to_person_bad]
        # )


if __name__ == "__main__":
    unittest.main()
