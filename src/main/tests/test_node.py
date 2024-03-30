import unittest

from objects.node import Node
from objects.property import Property


class TestNode(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.person_name = Property(name="name", type="str", csv_mapping="first_name", is_unique=True)
        cls.person_age = Property(name="age", type="str", csv_mapping="age", is_unique=False)
    
    def test_init(self) -> None:

        node = Node(label="Person", properties=[self.person_name, self.person_age])

        self.assertEqual(node.label, "Person")
        self.assertEqual(len(node.properties), 2)

    def test_properties(self) -> None:

        node = Node(label="Person", properties=[self.person_name, self.person_age])

        self.assertEqual(node.property_names, ["name", "age"])

    def test_unique_constraints(self) -> None:

        node = Node(label="Person", properties=[self.person_name, self.person_age])

        self.assertEqual(node.unique_constraints, ["name"])

    def test_property_column_mapping(self) -> None:

        node = Node(label="Person", properties=[self.person_name, self.person_age])

        self.assertEqual(node.property_column_mapping, {"name": "first_name", "age": "age"})

    def test_unique_constraints_column_mapping(self) -> None:

        node = Node(label="Person", properties=[self.person_name, self.person_age])

        self.assertEqual(node.unique_constraints_column_mapping, {"name": "first_name"})


