import unittest

from neo4j_runway.utils.naming_conventions import (
    fix_node_label,
    fix_property,
    fix_relationship_type,
    is_camel_case,
    is_mixed_case,
    is_pascal_case,
    is_snake_case,
)


class TestNamingConventions(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pass

    def test_fix_node_label(self) -> None:
        """
        Test applying Neo4j naming convention to a node label.
        """

        self.assertEqual(fix_node_label("Test_Label"), "TestLabel")
        self.assertEqual(fix_node_label("Test Label"), "TestLabel")
        self.assertEqual(fix_node_label("Test label"), "TestLabel")
        self.assertEqual(fix_node_label("Test"), "Test")
        self.assertEqual(fix_node_label("test"), "Test")
        self.assertEqual(fix_node_label("test_Label"), "TestLabel")
        self.assertEqual(fix_node_label("test_label"), "TestLabel")
        self.assertEqual(fix_node_label("testLabel"), "TestLabel")
        self.assertEqual(
            fix_node_label("TestLabelPascal_Snake"), "TestLabelPascalSnake"
        )
        self.assertEqual(fix_node_label("test_long_Title_long"), "TestLongTitleLong")

    def test_fix_relationship_type(self) -> None:
        """
        Test applying Neo4j naming convention to a relationship type.
        """

        self.assertEqual(fix_relationship_type("Test_Label"), "TEST_LABEL")
        self.assertEqual(fix_relationship_type("Test Label"), "TEST_LABEL")
        self.assertEqual(fix_relationship_type("Test label"), "TEST_LABEL")
        self.assertEqual(fix_relationship_type("test_Label"), "TEST_LABEL")
        self.assertEqual(fix_relationship_type("test_label"), "TEST_LABEL")
        self.assertEqual(fix_relationship_type("testLabel"), "TEST_LABEL")
        self.assertEqual(
            fix_relationship_type("TestLabelPascal_Snake"), "TEST_LABEL_PASCAL_SNAKE"
        )
        self.assertEqual(
            fix_relationship_type("test_long_title_long"), "TEST_LONG_TITLE_LONG"
        )
        self.assertEqual(fix_relationship_type("hasAddress_Three"), "HAS_ADDRESS_THREE")
        self.assertEqual(fix_relationship_type("TEST"), "TEST")
        self.assertEqual(fix_relationship_type("test"), "TEST")

    def test_fix_property(self) -> None:
        """
        Test applying Neo4j naming convention to a property name.
        """

        self.assertEqual(fix_property("Test_Label"), "testLabel")
        self.assertEqual(fix_property("Test Label"), "testLabel")
        self.assertEqual(fix_property("Test label"), "testLabel")
        self.assertEqual(fix_property("test"), "test")
        self.assertEqual(fix_property("Test"), "test")
        self.assertEqual(fix_property("test_Label"), "testLabel")
        self.assertEqual(fix_property("test_label"), "testLabel")
        self.assertEqual(fix_property("TestLabel"), "testLabel")
        self.assertEqual(fix_property("TestLabelPascalLong"), "testLabelPascalLong")
        self.assertEqual(fix_property("TestLabelPascal_Snake"), "testLabelPascalSnake")
        self.assertEqual(fix_property("test_long_title_long"), "testLongTitleLong")

    def test_is_camel_case(self) -> None:
        """
        Test determining if input is camel case.
        """

        self.assertFalse(is_camel_case("snake_case"))
        self.assertFalse(is_camel_case("Snake_Case"))
        self.assertFalse(is_camel_case("SNAKE_CASE"))
        self.assertTrue(is_camel_case("camelCase"))
        self.assertFalse(is_camel_case("PascalCase"))

    def test_is_pascal_case(self) -> None:
        """
        Test determining if input is Pascal case.
        """

        self.assertFalse(is_pascal_case("snake_case"))
        self.assertFalse(is_pascal_case("Snake_Case"))
        self.assertFalse(is_pascal_case("SNAKE_CASE"))
        self.assertFalse(is_pascal_case("camelCase"))
        self.assertTrue(is_pascal_case("PascalCase"))

    def test_is_snake_case(self) -> None:
        """
        Test determining if input is snake case.
        """

        self.assertTrue(is_snake_case("snake_case"))
        self.assertTrue(is_snake_case("snake_case_long_version_test"))
        self.assertTrue(is_snake_case("Snake_Case"))
        self.assertTrue(is_snake_case("SNAKE_CASE"))
        self.assertFalse(is_snake_case("camelCase"))
        self.assertFalse(is_snake_case("PascalCase"))

    def test_is_mixed_case(self) -> None:
        """
        Test determining if input is mix of camel, pascal or snake case.
        """

        self.assertTrue(is_mixed_case("camelPascal_snake"))
        self.assertTrue(is_mixed_case("camelPascal_Snake"))
        self.assertFalse(is_mixed_case("snake_case"))
        self.assertFalse(is_mixed_case("SCREAMING_SNAKE_CASE"))
        self.assertFalse(is_mixed_case("snake_Case"))
        self.assertFalse(is_mixed_case("camelCase"))
        self.assertFalse(is_mixed_case("PascalCase"))
        self.assertFalse(is_mixed_case("camel"))
        self.assertFalse(is_mixed_case("camelA"))

    def test_empty_input_is_case(self) -> None:
        """
        Test error when no input or empty string given.
        """

        with self.assertRaises(AssertionError):
            is_camel_case("")
        with self.assertRaises(AssertionError):
            is_snake_case("")
        with self.assertRaises(AssertionError):
            is_pascal_case("")
        with self.assertRaises(AssertionError):
            is_mixed_case("")


if __name__ == "__main__":
    unittest.main()
