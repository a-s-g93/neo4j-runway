import unittest

from ..objects.node import Node
from ..objects.property import Property
from ..objects.arrows import ArrowsNode


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

    def test_properties(self) -> None:

        node = Node(label="Person", properties=[self.person_name, self.person_age])

        self.assertEqual(node.property_names, ["name", "age"])

    def test_unique_properties(self) -> None:

        node = Node(label="Person", properties=[self.person_name, self.person_age])

        self.assertEqual(node.unique_properties, ["name"])

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
            caption="name",
            position={"x": 0, "y": 0},
            labels=["Person"],
            properties={"name": "first_name | str", "age": "age | int"},
        )

        node = Node(label="Person", properties=[self.person_name, self.person_age])

        self.assertEqual(node.label, "Person")
        self.assertEqual(len(node.properties), 2)
        print(arrows_node)
        node_from_arrows = Node.from_arrows(arrows_node=arrows_node)

        self.assertEqual(node_from_arrows.label, "Person")
        self.assertEqual(len(node_from_arrows.properties), 2)
        self.assertTrue(node_from_arrows.properties[0].is_unique)
        self.assertEqual(node_from_arrows.properties[0].type, "str")
        self.assertEqual(node_from_arrows.properties[1].type, "int")

    def test_parse_arrows_property(self) -> None:
        """
        Test the parsing of an arrows property to a standard property model.
        """

        to_parse = {"name": "name_col | str"}  # passes
        to_parse2 = {"notUnique": "nu_col|str"}  # passes
        to_parse3 = {
            "other": "other_col | STRING"
        }  # should pass, but replace the STRING type with str

        caption = "name, other, thisOne"

        parsed_prop1 = Node._parse_arrows_property(to_parse, caption)
        parsed_prop2 = Node._parse_arrows_property(to_parse2, caption)
        parsed_prop3 = Node._parse_arrows_property(to_parse3, caption)

        prop1 = Property(
            name="name", type="str", csv_mapping="name_col", is_unique=True
        )
        prop2 = Property(
            name="notUnique", type="str", csv_mapping="nu_col", is_unique=False
        )
        prop3 = Property(
            name="other", type="str", csv_mapping="other_col", is_unique=True
        )

        self.assertEqual(parsed_prop1, prop1)
        self.assertEqual(parsed_prop2, prop2)
        self.assertEqual(parsed_prop3, prop3)

        to_parse4 = {"name": "name_col"}
        prop4 = Property(
            name="name", type="unknown", csv_mapping="name_col", is_unique=False
        )

        self.assertEqual(Node._parse_arrows_property(to_parse4, ""), prop4)
        self.assertEqual(Node._parse_arrows_property(to_parse4, " adfwe"), prop4)


if __name__ == "__main__":
    unittest.main()
