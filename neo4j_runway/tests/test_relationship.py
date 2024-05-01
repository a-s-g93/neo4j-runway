import unittest

from ..objects.relationship import Relationship
from ..objects.property import Property
from ..objects.arrows import ArrowsRelationship


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

        self.assertEqual(relationship.unique_properties, ["current"])

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
        node_id_label_map = {"n0": "NodeA", "n1": "NodeB"}
        arrows_relationship = ArrowsRelationship(
            id="HAS_SIMILARNodeANodeB",
            type="HAS_SIMILAR",
            fromId="n0",
            toId="n1",
            properties={
                "score": "similarity_score | float",
                "current": "current | bool",
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
            node_id_label_map=node_id_label_map
        )

        self.assertEqual(relationship_from_arrows.type, arrows_relationship.type)
        self.assertEqual(len(relationship_from_arrows.properties), 2)
        self.assertEqual(relationship_from_arrows.source, node_id_label_map["n0"])
        self.assertEqual(relationship_from_arrows.target, node_id_label_map["n1"])
        self.assertFalse(relationship_from_arrows.properties[0].is_unique)
        self.assertEqual(relationship_from_arrows.properties[0].type, "float")
        self.assertEqual(relationship_from_arrows.properties[1].type, "bool")

    def test_parse_arrows_property(self) -> None:
        """
        Test the parsing of an arrows property to a standard property model.
        """

        to_parse = {"name": "name_col | str"}  # passes
        to_parse2 = {"notUnique": "nu_col|str"}  # passes
        to_parse3 = {
            "other": "other_col | STRING"
        }  # should pass, but replace the STRING type with str

        parsed_prop1 = Relationship._parse_arrows_property(to_parse)
        parsed_prop2 = Relationship._parse_arrows_property(to_parse2)
        parsed_prop3 = Relationship._parse_arrows_property(to_parse3)

        prop1 = Property(
            name="name", type="str", csv_mapping="name_col", is_unique=False
        )
        prop2 = Property(
            name="notUnique", type="str", csv_mapping="nu_col", is_unique=False
        )
        prop3 = Property(
            name="other", type="str", csv_mapping="other_col", is_unique=False
        )

        self.assertEqual(parsed_prop1, prop1)
        self.assertEqual(parsed_prop2, prop2)
        self.assertEqual(parsed_prop3, prop3)

        to_parse4 = {"name": "name_col"}
        prop4 = Property(
            name="name", type="unknown", csv_mapping="name_col", is_unique=False
        )

        self.assertEqual(Relationship._parse_arrows_property(to_parse4), prop4)
        self.assertEqual(Relationship._parse_arrows_property(to_parse4), prop4)


if __name__ == "__main__":
    unittest.main()
