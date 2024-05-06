import unittest

from ..objects.property import Property, TYPES_MAP_PYTHON_KEYS


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
            list(prop.keys()), ["name", "type", "csv_mapping", "is_unique"]
        )
        self.assertEqual(prop["csv_mapping"], "name")

    def test_neo4j_properties(self) -> None:
        """
        Test the Neo4j property mapping.
        """

        for k, v in TYPES_MAP_PYTHON_KEYS.items():
            self.assertEqual(
                Property(
                    name="city", type=k, csv_mapping="city", is_unique=False
                ).neo4j_type,
                v,
            )


if __name__ == "__main__":
    unittest.main()
