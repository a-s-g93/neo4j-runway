import unittest

from ..objects.node import Node
from ..objects.relationship import Relationship
from ..objects.property import Property
from ..objects.data_model import DataModel
from ..ingestion.generate_ingest import *
from ..tests.resources.ingestion_generation_answers import *


class TestIngestCodeGneration(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:

        prop_a_1 = Property(
            name="uniqueProp1", csv_mapping="unique_prop_1", type="str", is_unique=True
        )
        prop_a_2 = Property(
            name="prop1", csv_mapping="prop_1", type="str", is_unique=False
        )
        prop_a_3 = Property(
            name="uniqueProp3", csv_mapping="unique_prop_3", type="str", is_unique=True
        )
        prop_b_1 = Property(
            name="uniqueProp2", csv_mapping="unique_prop_2", type="str", is_unique=True
        )
        prop_b_2 = Property(
            name="prop2", csv_mapping="prop_2", type="str", is_unique=False
        )
        prop_b_3 = Property(
            name="prop3", csv_mapping="prop_3", type="str", is_unique=False
        )
        prop_rel_1 = Property(
            name="relProp", csv_mapping="rel_prop", type="int", is_unique=False
        )

        cls.node_a = Node(label="NodeA", properties=[prop_a_1, prop_a_2, prop_a_3])
        cls.node_b = Node(label="NodeB", properties=[prop_b_1, prop_b_2, prop_b_3])
        cls.rel_1 = Relationship(
            type="HAS_RELATIONSHIP",
            properties=[prop_rel_1],
            source=cls.node_a.label,
            target=cls.node_b.label,
        )

        cls.data_model = DataModel(
            nodes=[cls.node_a, cls.node_b], relationships=[cls.rel_1]
        )

        cls.code_gen = IngestionGenerator(
            data_model=cls.data_model,
            username="neo4j",
            password="password",
            uri="bolt://address:7687",
            database="testdb",
            csv_name="test.csv",
            csv_dir="test_dir/",
            file_output_dir="",
        )

    def test_generate_constraints_key(self) -> None:
        """
        Generate the key for a unique constraint.
        """

        label = self.node_a.label
        unique_props = self.node_a.unique_properties
        self.assertEqual(
            generate_constraints_key(
                label_or_type=label, unique_property=unique_props[0]
            ),
            constraints_key_a_1,
        )
        self.assertEqual(
            generate_constraints_key(
                label_or_type=label, unique_property=unique_props[1]
            ),
            constraints_key_a_3,
        )

        label = self.node_b.label
        unique_props = self.node_b.unique_properties
        self.assertEqual(
            generate_constraints_key(
                label_or_type=label, unique_property=unique_props[0]
            ),
            constraints_key_b,
        )

    def test_generate_constraint(self) -> None:
        """
        Generate a constraint string.
        """

        label = self.node_a.label
        unique_props = self.node_a.unique_properties
        self.assertEqual(
            generate_constraint(label_or_type=label, unique_property=unique_props[0]),
            constraint_a_1,
        )
        self.assertEqual(
            generate_constraint(label_or_type=label, unique_property=unique_props[1]),
            constraint_a_3,
        )

        label = self.node_b.label
        unique_props = self.node_b.unique_properties
        self.assertEqual(
            generate_constraint(label_or_type=label, unique_property=unique_props[0]),
            constraint_b,
        )

    def test_generate_match_node_clause(self) -> None:
        """
        Generate a MATCH node clause.
        """

        self.assertEqual(
            generate_match_node_clause(node=self.node_a),
            match_node_a,
        )

        self.assertEqual(
            generate_match_node_clause(node=self.node_b),
            match_node_b,
        )

    def test_generate_set_property(self) -> None:
        """
        Generate a set property string.
        """

        unique_map = self.node_a.unique_properties_column_mapping
        prop_map = self.node_a.property_column_mapping
        for k in unique_map.keys():
            del prop_map[k]
        self.assertEqual(
            generate_set_property(property_column_mapping=prop_map), set_properties_a
        )

        unique_map = self.node_b.unique_properties_column_mapping
        prop_map = self.node_b.property_column_mapping
        for k in unique_map.keys():
            del prop_map[k]
        self.assertEqual(
            generate_set_property(property_column_mapping=prop_map), set_properties_b
        )

    def test_generate_set_unique_property(self) -> None:
        """
        Generate the unique properties to match a node on within a MERGE statement.
        """

        self.assertEqual(
            generate_set_unique_property(
                unique_properties_column_mapping=self.node_a.unique_properties_column_mapping
            ),
            set_unique_property_a,
        )
        self.assertEqual(
            generate_set_unique_property(
                unique_properties_column_mapping=self.node_b.unique_properties_column_mapping
            ),
            set_unique_property_b,
        )

    def test_generate_merge_node_clause_standard(self) -> None:
        """
        Generate a MERGE node clause.
        """

        self.assertEqual(
            generate_merge_node_clause_standard(node=self.node_a),
            merge_node_standard_a,
        )

    def test_generate_merge_node_load_csv_clause(self) -> None:
        """
        Generate a MERGE node clause for the LOAD CSV method.
        """

        self.assertEqual(
            generate_merge_node_load_csv_clause(
                node=self.node_b,
                csv_name="test.csv"
            ),
            merge_node_load_csv_b,
        )

    def test_generate_merge_relationship_clause_standard(self) -> None:
        """
        Generate a MERGE relationship clause.
        """

        self.assertEqual(
            generate_merge_relationship_clause_standard(
                relationship=self.rel_1,
                source_node=self.node_a,
                target_node=self.node_b,
            ),
            merge_relationship_standard,
        )

    def test_generate_merge_relationship_load_csv_clause(self) -> None:
        """
        Generate a MERGE relationship clause for the LOAD CSV method.
        """

        self.assertEqual(
            generate_merge_relationship_load_csv_clause(
                relationship=self.rel_1,
                source_node=self.node_a,
                target_node=self.node_b,
                csv_name="test.csv",
                batch_size=50,
            ),
            merge_relationship_load_csv,
        )

    def test_generate_pyingest_string(self) -> None:
        """
        Test PyIngest string generation.
        """

        pass

    def test_generate_load_csv_string(self) -> None:
        """
        Test LOAD_CSV string generation.
        """

        pass


if __name__ == "__main__":
    unittest.main()
