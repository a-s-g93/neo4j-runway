import unittest

from neo4j_runway.models.core.property import Property
from neo4j_runway.resources.mappings import TYPES_MAP_PYTHON_TO_NEO4J


class TestProperty(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pass

    def test_init(self) -> None:
        """
        Test input for init.
        """

        self.assertIsInstance(
            Property(name="name", type="str", csv_mapping="name", is_unique=True),
            Property,
        )
        self.assertIsInstance(
            Property(name="street", type="str", csv_mapping="street", is_unique=False),
            Property,
        )

    def test_init_with_neo4j_type(self) -> None:
        p = Property(
            name="street", type="STRING", csv_mapping="street", is_unique=False
        )
        self.assertEqual(p.type, "str")

    def test_float64_type(self) -> None:
        p = Property(
            name="street", type="float64", csv_mapping="street", is_unique=False
        )
        self.assertEqual(p.type, "float")

    def test_bad_type(self) -> None:
        with self.assertRaises(ValueError):
            Property(name="name", type="hashmap", csv_mapping="name", is_unique=True)

        with self.assertRaises(ValueError):
            Property(name="name", type="dictionary", csv_mapping="name", is_unique=True)

    def test_to_dict(self) -> None:
        """
        Test dict property.
        """

        prop = Property(
            name="name", type="str", csv_mapping="name", is_unique=True
        ).model_dump()

        self.assertEqual(
            list(prop.keys()),
            [
                "name",
                "type",
                "csv_mapping",
                "csv_mapping_other",
                "is_unique",
                "part_of_key",
            ],
        )
        self.assertEqual(prop["csv_mapping"], "name")

    def test_neo4j_properties(self) -> None:
        """
        Test the Neo4j property mapping.
        """

        for k, v in TYPES_MAP_PYTHON_TO_NEO4J.items():
            self.assertEqual(
                Property(
                    name="city", type=k, csv_mapping="city", is_unique=False
                ).neo4j_type,
                v,
            )

    def test_parse_arrows_property(self) -> None:
        """
        Test the parsing of an arrows property to a standard property model.
        """

        to_parse = {"name": "name_col | str | unique"}  # passes
        to_parse2 = {"notUnique": "nu_col|str"}  # passes
        to_parse3 = {
            "other": "other_col | STRING | unique"
        }  # should pass, but replace the STRING type with str

        caption = "name, other, thisOne"

        parsed_prop1 = Property.from_arrows(to_parse, caption)
        parsed_prop2 = Property.from_arrows(to_parse2, caption)
        parsed_prop3 = Property.from_arrows(to_parse3)

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

        self.assertEqual(Property.from_arrows(to_parse4, ""), prop4)
        self.assertEqual(Property.from_arrows(to_parse4, " adfwe"), prop4)


if __name__ == "__main__":
    unittest.main()
