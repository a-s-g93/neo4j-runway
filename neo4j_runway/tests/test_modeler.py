import unittest

from graphviz import Digraph

from objects.node import Node
from objects.relationship import Relationship
from objects.property import Property
from objects.data_model import DataModel
from modeler.modeler import GraphDataModeler

USER_GENERATED_INPUT = {
    "General Description": "This is data on some interesting data.",
    "id": "unique id for a node.",
    "feature_1": "this is a feature",
    "feature_2": "this is also a feature",
}

USER_GENERATED_INPUT_BAD = {
    # 'General Description': 'This is data on some interesting data.',
    "id": "unique id for a node.",
    "feature_1": "this is a feature",
    "feature_2": "this is also a feature",
}

person_name = Property(name="name", type="str", csv_mapping="name", is_unique=True)
person_age = Property(name="age", type="str", csv_mapping="age", is_unique=False)
address_street = Property(
    name="street", type="str", csv_mapping="street", is_unique=False
)
address_city = Property(name="city", type="str", csv_mapping="city", is_unique=False)
pet_name = Property(name="name", type="str", csv_mapping="pet_name", is_unique=False)
pet_kind = Property(name="kind", type="str", csv_mapping="pet", is_unique=False)
toy_name = Property(name="name", type="str", csv_mapping="toy", is_unique=True)
toy_kind = Property(name="kind", type="str", csv_mapping="toy_type", is_unique=False)

nodes = [
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

relationships = [
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

nodes2 = nodes + [
    Node(
        label="Test",
        properties=[
            Property(name="name", type="str", csv_mapping="test", is_unique=True)
        ],
    )
]
data_model = DataModel(nodes=nodes, relationships=relationships)
data_model2 = DataModel(nodes=nodes2, relationships=relationships)


class TestGraphDataModler(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.gdm = GraphDataModeler(
            llm="llm",
            user_input=USER_GENERATED_INPUT,
            discovery="discovery",
            general_data_description="desc",
            categorical_data_description="desc",
            numeric_data_description="desc",
            feature_descriptions="desc",
        )
        cls.gdm.model_history = [data_model, data_model2, data_model]

    def test_get_model(self) -> None:
        """
        Test get model logic.
        """

        self.assertEqual(self.gdm.get_model(version=2, as_dict=False), data_model2)
        self.assertEqual(
            self.gdm.get_model(version=1, as_dict=True), data_model.model_dump()
        )
        self.assertEqual(self.gdm.get_model(version=-3, as_dict=False), data_model)

        with self.assertRaises(AssertionError):
            self.gdm.get_model(version=4, as_dict=False)

        with self.assertRaises(AssertionError):
            self.gdm.get_model(version=0, as_dict=False)

        with self.assertRaises(AssertionError):
            self.gdm.get_model(version=-4, as_dict=True)

    def test_current_model_viz(self) -> None:
        """
        Test viz returns Digraph.
        """

        self.assertIsInstance(self.gdm.current_model_viz, Digraph)

    def test_discovery_warning(self) -> None:
        """
        Test warning is triggered if no discovery passed to constructor.
        """

        with self.assertWarns(Warning):
            GraphDataModeler(
                llm="llm",
                user_input=USER_GENERATED_INPUT,
                # discovery="discovery",
                general_data_description="desc",
                categorical_data_description="desc",
                numeric_data_description="desc",
                feature_descriptions="desc",
            )

    def test_no_general_info_in_user_input(self) -> None:
        """
        Test error if no general description of data is present in user info.
        """

        with self.assertRaises(AssertionError):
            gdm = GraphDataModeler(
                llm="llm",
                user_input=USER_GENERATED_INPUT_BAD,
                discovery="discovery",
                general_data_description="desc",
                categorical_data_description="desc",
                numeric_data_description="desc",
                feature_descriptions="desc",
            )


if __name__ == "__main__":
    unittest.main()
