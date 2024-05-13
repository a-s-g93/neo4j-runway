import unittest

from ..objects import Node, ArrowsRelationship
from ..objects.relationship import _get_relationship_csv_name


nodes = [
    Node(label="NodeA", properties=[], csv_name="CSV_A"),
    Node(label="NodeB", properties=[], csv_name="CSV_B"),
    Node(label="NodeC", properties=[], csv_name="CSV_A"),
]
arrows_rel = ArrowsRelationship(
    type="REL", id="REL", fromId="NodeA", toId="NodeC", properties={}
)


class TestGetRelationshipCSVName(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        pass

    def test_get_relationship_csv_name_valid(self) -> None:
        """
        Test the function.
        """

        res = _get_relationship_csv_name(
            source="NodeA", target="NodeC", nodes_dict={n.label: n for n in nodes}
        )

        self.assertEqual(res, "CSV_A")

    def test_get_relationship_csv_name_invalid(self) -> None:
        """
        source and target csv's aren't equal.
        """

        res = _get_relationship_csv_name(
            source="NodeA", target="NodeC", nodes_dict={n.label: n for n in nodes[:2]}
        )

        self.assertEqual(res, "")
