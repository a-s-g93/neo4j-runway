import unittest

from objects.node import Node
from objects.relationship import Relationship
from objects.property import Property
from objects.data_model import DataModel


class TestIngestCodeGneration(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:

        prop_a_1 = Property(
            name="uniqueProp1", csv_mapping="unique_prop_1", type="str", is_unique=True
        )
        prop_a_2 = Property(
            name="prop1", csv_mapping="prop_1", type="str", is_unique=False
        )
        prop_b_1 = Property(
            name="uniqueProp2", csv_mapping="unique_prop_2", type="str", is_unique=True
        )
        prop_b_2 = Property(
            name="prop2", csv_mapping="prop_2", type="str", is_unique=False
        )
        prop_rel_1 = Property(
            name="relProp", csv_mapping="rel_prop", type="int", is_unique=False
        )

        cls.node_a = Node(label="NodeA", properties=[prop_a_1, prop_a_2])
        cls.node_b = Node(label="NodeB", properties=[prop_b_1, prop_b_2])
        cls.rel_1 = Relationship(
            type="HAS_RELATIONSHIP",
            properties=[prop_rel_1],
            source=cls.node_a,
            target=cls.node_b,
        )

        cls.data_model = DataModel(
            nodes=[cls.node_a, cls.node_b], relationships=[cls.rel_1]
        )

    def test_generate_constraints_key(self) -> None:
        """
        Generate the key for a unique constraint.
        """

        pass

    def test_generate_constraint(self) -> None:
        """
        Generate a constrant string.
        """

        pass

    def test_generate_match_node_clause(self) -> None:
        """
        Generate a MATCH node clause.
        """

        pass

    def test_generate_set_property(self) -> None:
        """
        Generate a set property string.
        """

        pass

    def test_generate_set_unique_property(self) -> None:
        """
        Generate the unique properties to match a node on within a MERGE statement.
        """

        pass

    def test_generate_merge_node_clause_standard(self) -> None:
        """
        Generate a MERGE node clause.
        """

        pass

    def test_generate_merge_node_load_csv_clause() -> None:
        """
        Generate a MERGE node clause for the LOAD CSV method.
        """

        pass

    def test_generate_merge_relationship_clause_standard(self) -> None:
        """
        Generate a MERGE relationship clause.
        """
        pass

    def test_generate_merge_relationship_load_csv_clause(self) -> None:
        """
        Generate a MERGE relationship clause for the LOAD CSV method.
        """

        pass
