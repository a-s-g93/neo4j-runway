import unittest

from objects.relationship import Relationship
from objects.property import Property

class TestRelationship(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.prop1 = Property(name="score", type="float", csv_mapping="similarity_score", is_unique=False)
        cls.prop2 = Property(name="current", type="bool", csv_mapping="current", is_unique=True)
        cls.source = "NodeA"
        cls.target = "NodeB"
    
    def test_init(self) -> None:

        relationship = Relationship(type="HAS_SIMILAR", properties=[self.prop1, self.prop2], source=self.source, target=self.target)

        self.assertEqual(relationship.type, "HAS_SIMILAR")
        self.assertEqual(len(relationship.properties), 2)

    def test_properties(self) -> None:

        relationship = Relationship(type="HAS_SIMILAR", properties=[self.prop1, self.prop2], source=self.source, target=self.target)

        self.assertEqual(relationship.property_names, ["score", "current"])

    def test_unique_constraints(self) -> None:

        relationship = Relationship(type="HAS_SIMILAR", properties=[self.prop1, self.prop2], source=self.source, target=self.target)

        self.assertEqual(relationship.unique_constraints, ["current"])

    def test_property_column_mapping(self) -> None:

        relationship = Relationship(type="HAS_SIMILAR", properties=[self.prop1, self.prop2], source=self.source, target=self.target)

        self.assertEqual(relationship.property_column_mapping, {"score": "similarity_score", "current": "current"})

    def test_unique_constraints_column_mapping(self) -> None:

        relationship = Relationship(type="HAS_SIMILAR", properties=[self.prop1, self.prop2], source=self.source, target=self.target)

        self.assertEqual(relationship.unique_constraints_column_mapping, {"current": "current"})


