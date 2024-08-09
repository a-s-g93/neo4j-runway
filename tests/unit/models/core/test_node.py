import unittest

from neo4j_runway.models import Node, Property
from neo4j_runway.models.arrows import ArrowsNode


class TestNode(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.person_name = Property(
            name="name", type="str", csv_mapping="first_name", is_unique=True
        )
        cls.person_age = Property(
            name="age", type="str", csv_mapping="age", is_unique=False
        )

    def test_init(self) -> None:
        node = Node(label="Person", properties=[self.person_name, self.person_age])

        self.assertEqual(node.label, "Person")
        self.assertEqual(len(node.properties), 2)

    def test_get_property(self) -> None:
        node = Node(label="Person", properties=[self.person_name, self.person_age])


        prop = node.get_property("age")
        self.assertIsNotNone(prop)
        self.assertEqual(prop.name, "age")


    def test_properties(self) -> None:
        node = Node(label="Person", properties=[self.person_name, self.person_age])

        self.assertEqual(node.property_names, ["name", "age"])

    def test_unique_properties(self) -> None:
        node = Node(label="Person", properties=[self.person_name, self.person_age])

        self.assertEqual(node.unique_properties, [self.person_name])

    def test_property_column_mapping(self) -> None:
        node = Node(label="Person", properties=[self.person_name, self.person_age])

        self.assertEqual(
            node.property_column_mapping, {"name": "first_name", "age": "age"}
        )

    def test_unique_properties_column_mapping(self) -> None:
        node = Node(label="Person", properties=[self.person_name, self.person_age])

        self.assertEqual(node.unique_properties_column_mapping, {"name": "first_name"})

    def test_from_arrows(self) -> None:
        """
        Test init from arrows node.
        """

        arrows_node = ArrowsNode(
            id="Person",
            caption="",
            position={"x": 0, "y": 0},
            labels=["Person"],
            properties={"name": "first_name | str | unique", "age": "age | int"},
        )

        node = Node(label="Person", properties=[self.person_name, self.person_age])

        self.assertEqual(node.label, "Person")
        self.assertEqual(len(node.properties), 2)
        node_from_arrows = Node.from_arrows(arrows_node=arrows_node)

        self.assertEqual(node_from_arrows.label, "Person")
        self.assertEqual(len(node_from_arrows.properties), 2)
        self.assertTrue(node_from_arrows.properties[0].is_unique)
        self.assertEqual(node_from_arrows.properties[0].type, "str")
        self.assertEqual(node_from_arrows.properties[1].type, "int")

    def test_from_arrows_with_ignored_property(self) -> None:
        """
        Test init from arrows node with an ignored property.
        """

        arrows_node = ArrowsNode(
            id="Person",
            caption="",
            position={"x": 0, "y": 0},
            labels=["Person"],
            properties={
                "name": "first_name | str | unique",
                "age": "age | int | ignore",
            },
        )

        node = Node(label="Person", properties=[self.person_name])

        self.assertEqual(node.label, "Person")
        self.assertEqual(len(node.properties), 1)
        node_from_arrows = Node.from_arrows(arrows_node=arrows_node)

        self.assertEqual(len(node_from_arrows.properties), 1)

    def test_validate_node_keys(self) -> None:
        node = Node(
            label="nodeA",
            properties=[
                Property(
                    name="nkey",
                    type="str",
                    csv_mapping="nkey",
                    is_unique=False,
                    part_of_key=True,
                )
            ],
        )

        errors = node.validate_properties(csv_columns=["nkey"])
        message = "The node nodeA has a node key on only one property nkey. Node keys must exist on two or more properties."
        self.assertIn(message, errors)

    def test_get_property(self) -> None:
        """
        Test get_property method.
        """
        # Create sample properties
        person_height = Property(name="height", type="int", csv_mapping="height", is_unique=False)
        person_weight = Property(name="weight", type="int", csv_mapping="weight", is_unique=False)
        person_name = Property(name="name", type="str", csv_mapping="name", is_unique=True)

        node = Node(label="Person", properties=[person_height, person_weight, person_name])

        retrieved_property = node.get_property("height")
        self.assertIsNotNone(retrieved_property)
        self.assertEqual(retrieved_property.name, "height")

        unique_property = node.get_property("name")
        self.assertIsNone(unique_property)

        # Test retrieving a non-existing property (should return None)
        non_existing_property = node.get_property("age")
        self.assertIsNone(non_existing_property)

    def test_mutate_property(self) -> None:
        """
        Test mutate_property method.
        """

        person_height = Property(name="height", type="int", csv_mapping="height", is_unique=False)
        person_weight = Property(name="weight", type="int", csv_mapping="weight", is_unique=False)
        person_name = Property(name="name", type="str", csv_mapping="name", is_unique=True)

        node = Node(label="Person", properties=[person_height, person_weight, person_name])

        updated_property = node.mutate_property("height", type="float", csv_mapping="new_height")
        self.assertEqual(updated_property.name, "height")
        self.assertEqual(updated_property.type, "float")
        self.assertEqual(updated_property.csv_mapping, "new_height")

        property_in_node = node.get_property("height")
        self.assertEqual(property_in_node.type, "float")
        self.assertEqual(property_in_node.csv_mapping, "new_height")

        with self.assertRaises(ValueError) as context:
            node.mutate_property("nonexistent", type="str")
        self.assertEqual(str(context.exception), "Property with name nonexistent not found.")

        with self.assertRaises(ValueError) as context:
            node.mutate_property("weight", invalid_attr="value")
        self.assertEqual(str(context.exception), "Property has no attribute 'invalid_attr'.")

    def test_add_property(self) -> None:
        """
        Test add_property method.
        """
        person_height = Property(name="height", type="int", csv_mapping="height", is_unique=False)
        person_weight = Property(name="weight", type="int", csv_mapping="weight", is_unique=False)

        node = Node(label="Person", properties=[person_height, person_weight])

        new_property = Property(name="age", type="int", csv_mapping="age", is_unique=False)
        node.add_property(new_property)
        self.assertEqual(len(node.properties), 3)
        self.assertEqual(node.get_property("age"), new_property)

        with self.assertRaises(ValueError) as context:
            duplicate_property = Property(name="height", type="float", csv_mapping="new_height")
            node.add_property(duplicate_property)
        self.assertEqual(str(context.exception), "Property with name 'height' already exists.")

    def test_set_property(self) -> None:
        """
        Test set_property method.
        """
        person_height = Property(name="height", type="int", csv_mapping="height", is_unique=False)
        person_weight = Property(name="weight", type="int", csv_mapping="weight", is_unique=False)

        node = Node(label="Person", properties=[person_height, person_weight])

        new_property = node.set_property(name="age", type="int", csv_mapping="age")
        self.assertEqual(len(node.properties), 3)
        self.assertEqual(new_property.name, "age")
        self.assertEqual(new_property.type, "int")
        self.assertEqual(new_property.csv_mapping, "age")

        updated_property = node.set_property(name="height", type="float", csv_mapping="new_height")
        self.assertEqual(len(node.properties), 3)
        self.assertEqual(updated_property.name, "height")
        self.assertEqual(updated_property.type, "float")
        self.assertEqual(updated_property.csv_mapping, "new_height")

        with self.assertRaises(ValueError) as context:
            node.set_property(name="height", type="float", invalid_attr="value")
        self.assertEqual(str(context.exception), "Property has no attribute 'invalid_attr'.")


if __name__ == "__main__":
    unittest.main()
