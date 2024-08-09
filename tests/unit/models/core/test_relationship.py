import unittest

from neo4j_runway.models import Property, Relationship
from neo4j_runway.models.arrows import ArrowsRelationship


class TestRelationship(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.prop1 = Property(
            name="score", type="float", csv_mapping="similarity_score", is_unique=False
        )
        cls.prop2 = Property(
            name="current", type="bool", csv_mapping="current", is_unique=True
        )
        cls.source = "NodeA"
        cls.target = "NodeB"

    def test_init(self) -> None:
        relationship = Relationship(
            type="HAS_SIMILAR",
            properties=[self.prop1, self.prop2],
            source=self.source,
            target=self.target,
        )

        self.assertEqual(relationship.type, "HAS_SIMILAR")
        self.assertEqual(len(relationship.properties), 2)

    def test_properties(self) -> None:
        relationship = Relationship(
            type="HAS_SIMILAR",
            properties=[self.prop1, self.prop2],
            source=self.source,
            target=self.target,
        )

        self.assertEqual(relationship.property_names, ["score", "current"])

    def test_unique_properties(self) -> None:
        relationship = Relationship(
            type="HAS_SIMILAR",
            properties=[self.prop1, self.prop2],
            source=self.source,
            target=self.target,
        )

        self.assertEqual(relationship.unique_properties, [self.prop2])

    def test_property_column_mapping(self) -> None:
        relationship = Relationship(
            type="HAS_SIMILAR",
            properties=[self.prop1, self.prop2],
            source=self.source,
            target=self.target,
        )

        self.assertEqual(
            relationship.property_column_mapping,
            {"score": "similarity_score", "current": "current"},
        )

    def test_unique_properties_column_mapping(self) -> None:
        relationship = Relationship(
            type="HAS_SIMILAR",
            properties=[self.prop1, self.prop2],
            source=self.source,
            target=self.target,
        )

        self.assertEqual(
            relationship.unique_properties_column_mapping, {"current": "current"}
        )

    def test_from_arrows(self) -> None:
        """
        Test init from arrows node.
        """
        node_id_to_label_map = {"n0": "NodeA", "n1": "NodeB"}
        arrows_relationship = ArrowsRelationship(
            id="HAS_SIMILARNodeANodeB",
            type="HAS_SIMILAR",
            fromId="n0",
            toId="n1",
            properties={
                "score": "similarity_score | float",
                "current": "current | bool",
                "csv": "test.csv",
            },
        )

        relationship = Relationship(
            type="HAS_SIMILAR",
            properties=[self.prop1, self.prop2],
            source=self.source,
            target=self.target,
        )

        self.assertEqual(relationship.type, "HAS_SIMILAR")
        self.assertEqual(len(relationship.properties), 2)

        relationship_from_arrows = Relationship.from_arrows(
            arrows_relationship=arrows_relationship,
            node_id_to_label_map=node_id_to_label_map,
        )

        self.assertEqual(relationship_from_arrows.type, arrows_relationship.type)
        self.assertEqual(len(relationship_from_arrows.properties), 2)
        self.assertEqual(relationship_from_arrows.source, node_id_to_label_map["n0"])
        self.assertEqual(relationship_from_arrows.target, node_id_to_label_map["n1"])
        self.assertFalse(relationship_from_arrows.properties[0].is_unique)
        self.assertEqual(relationship_from_arrows.properties[0].type, "float")
        self.assertEqual(relationship_from_arrows.properties[1].type, "bool")

    def test_validate_relationship_keys(self) -> None:
        rel = Relationship(
            type="relA",
            properties=[
                Property(
                    name="rkey",
                    type="str",
                    csv_mapping="rkey",
                    is_unique=False,
                    part_of_key=True,
                )
            ],
            source="A",
            target="B",
        )

        errors = rel.validate_properties(csv_columns=["rkey"])
        message = "The relationship relA has a relationship key on only one property rkey. Relationship keys must exist on two or more properties."
        self.assertIn(message, errors)

    def test_get_property(self) -> None:
        relationship = Relationship(
            type="HAS_SIMILAR",
            properties=[self.prop1, self.prop2],
            source=self.source,
            target=self.target,
        )

        self.assertEqual(relationship.get_property("score"), self.prop1)
        self.assertEqual(relationship.get_property("current"), self.prop2)

        self.assertIsNone(relationship.get_property("non_existent"))

    def test_add_property(self) -> None:
        """
        Test adding a new property to the relationship.
        """
        self.relationship.add_property(self.prop3)
        self.assertIn(self.prop3, self.relationship.properties)
        self.assertEqual(len(self.relationship.properties), 3)

        with self.assertRaises(ValueError) as context:
            self.relationship.add_property(self.prop1)
        self.assertEqual(
            str(context.exception),
            f"Property with name '{self.prop1.name}' already exists."
        )


if __name__ == "__main__":
    unittest.main()
