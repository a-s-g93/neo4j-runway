import unittest

from neo4j_runway.models import DataModel, Node, Property, Relationship
from tests.resources.answers.data_model_yaml import data_model_dict, data_model_yaml


class TestDataModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.columns = [
            "name",
            "age",
            "street",
            "city",
            "pet_name",
            "pet",
            "toy",
            "toy_type",
        ]

        person_name = Property(
            name="name", type="str", csv_mapping="name", is_unique=True
        )
        person_age = Property(
            name="age", type="str", csv_mapping="age", is_unique=False
        )
        address_street = Property(
            name="street", type="str", csv_mapping="street", is_unique=False
        )
        address_city = Property(
            name="city", type="str", csv_mapping="city", is_unique=False
        )
        pet_name = Property(
            name="name", type="str", csv_mapping="pet_name", is_unique=False
        )
        pet_kind = Property(name="kind", type="str", csv_mapping="pet", is_unique=False)
        toy_name = Property(name="name", type="str", csv_mapping="toy", is_unique=True)
        toy_kind = Property(
            name="kind", type="str", csv_mapping="toy_type", is_unique=False
        )

        cls.good_nodes = [
            Node(
                label="Person",
                properties=[person_name, person_age],
            ),
            Node(
                label="Address",
                properties=[address_street, address_city],
            ),
            Node(
                label="Pet",
                properties=[pet_name, pet_kind],
            ),
            Node(
                label="Toy",
                properties=[toy_name, toy_kind],
            ),
        ]

        cls.good_relationships = [
            Relationship(
                type="HAS_ADDRESS",
                properties=[],
                source="Person",
                target="Address",
            ),
            Relationship(
                type="KNOWS",
                properties=[],
                source="Person",
                target="Person",
            ),
            Relationship(
                type="HAS_PET",
                properties=[],
                source="Person",
                target="Pet",
            ),
            Relationship(
                type="PLAYS_WITH",
                properties=[],
                source="Pet",
                target="Toy",
            ),
        ]
        cls.bad_relationships = cls.good_relationships + [
            Relationship(
                type="BAD",
                properties=[],
                source="Dog",
                target="Toy",
            )
        ]
        cls.bad_nodes = cls.good_nodes + [
            Node(
                label="Toy",
                properties=[toy_name, toy_kind],
            )
        ]


    def test_bad_init(self) -> None:
        """
        Test bad input for init.
        """

        test_model = DataModel(
            nodes=self.bad_nodes, relationships=self.bad_relationships
        )
        validation = test_model.validate_model(csv_columns=self.columns)
        self.assertFalse(validation["valid"])
        self.assertIn("BAD", validation["message"].split())
        self.assertIn("Dog", validation["message"].split())
        self.assertIn("source", validation["message"].split())

    def test_good_init(self) -> None:
        """
        This input should pass.
        """

        # valid
        self.assertIsInstance(
            DataModel(nodes=self.good_nodes, relationships=self.good_relationships),
            DataModel,
        )

    def test_to_dict(self) -> None:
        """
        Test model_dump property.
        """

        test_model = DataModel(
            nodes=self.good_nodes, relationships=self.good_relationships
        )

        test_dict = test_model.model_dump()

        self.assertEqual(list(test_dict.keys()), ["nodes", "relationships", "metadata"])
        self.assertEqual(
            list(test_dict["nodes"][0].keys()), ["label", "properties", "csv_name"]
        )
        self.assertEqual(
            list(test_dict["relationships"][0].keys()),
            ["type", "properties", "source", "target", "csv_name"],
        )

    def test_neo4j_naming_conventions(self) -> None:
        """
        Test renaming labels, types and properties to Neo4j naming conventions.
        """

        prop1 = Property(
            name="Name",
            type="str",
            csv_mapping="name",
            csv_mapping_other="knows_person",
            is_unique=True,
        )
        prop2 = Property(
            name="person_age", type="int", csv_mapping="age", is_unique=False
        )
        prop3 = Property(
            name="CurrentStreet", type="str", csv_mapping="street", is_unique=True
        )
        prop4 = Property(
            name="favorite_score", type="int", csv_mapping="favorite", is_unique=False
        )

        name_conv_nodes = [
            Node(
                label="person",
                properties=[prop1, prop2],
            ),
            Node(
                label="current_Address",
                properties=[prop3],
            ),
        ]

        name_conv_relationships = [
            Relationship(
                type="has_address",
                properties=[prop4],
                source="Person",
                target="current_address",
            ),
            Relationship(
                type="HasSecondAddress",
                properties=[prop4],
                source="person",
                target="current_Address",
            ),
            Relationship(
                type="hasAddress_Three",
                properties=[prop4],
                source="Person",
                target="CURRENT_ADDRESS",
            ),
        ]

        dm = DataModel(
            nodes=name_conv_nodes,
            relationships=name_conv_relationships,
            use_neo4j_naming_conventions=False,
        )
        dm.apply_neo4j_naming_conventions()

        self.assertEqual(set(dm.node_labels), {"Person", "CurrentAddress"})
        self.assertEqual(
            set(dm.relationship_types),
            {"HAS_ADDRESS", "HAS_SECOND_ADDRESS", "HAS_ADDRESS_THREE"},
        )
        for rel in dm.relationships:
            self.assertIn(rel.source, ["Person", "CurrentAddress"])
            self.assertIn(rel.target, ["Person", "CurrentAddress"])

    def test_from_arrows_init(self) -> None:
        """
        Test init from arrows json file.
        """

        data_model = DataModel.from_arrows(
            file_path="tests/resources/data_models/arrows-data-model.json"
        )

        self.assertTrue(data_model.nodes[0].properties[0].is_unique)
        self.assertEqual(data_model.nodes[0].properties[1].type, "int")
        self.assertEqual(data_model.nodes[0].label, "Person")

    def test_to_yaml_string(self) -> None:
        """
        Test data model output to yaml format string.
        """

        data_model = DataModel(
            nodes=data_model_dict["nodes"],
            relationships=data_model_dict["relationships"],
        )
        self.maxDiff = None
        self.assertEqual(data_model.to_yaml(write_file=False), data_model_yaml)

    def test_data_model_with_multi_csv_from_arrows(self) -> None:
        data_model = DataModel.from_arrows(
            "tests/resources/data_models/people-pets-arrows-multi-csv.json"
        )

        self.assertEqual(data_model.relationships[-1].csv_name, "shelters.csv")
        self.assertEqual(data_model.relationships[0].csv_name, "pets-arrows.csv")
        self.assertEqual(data_model.nodes[0].csv_name, "pets-arrows.csv")

    def test_data_model_with_multi_csv_from_solutions_workbench(self) -> None:
        pass

    def test_get_node(self) -> None:
        """
        Test get_node method.
        """
        test_model = DataModel(nodes=self.good_nodes, relationships=self.good_relationships)

        node = test_model.get_node("Person")
        self.assertIsNotNone(node)
        self.assertEqual(node.label, "Person")

        node = test_model.get_node("NonExistingNode")
        self.assertIsNone(node)

    def test_get_relationship(self) -> None:
        """
        Test get_relationship method.
        """
        test_model = DataModel(nodes=self.good_nodes, relationships=self.good_relationships)

        relationship = test_model.get_relationship("HAS_ADDRESS")
        self.assertIsNotNone(relationship)
        self.assertEqual(relationship.type, "HAS_ADDRESS")

        relationship = test_model.get_relationship("NON_EXISTING_REL")
        self.assertIsNone(relationship)

    def test_set_node(self) -> None:
        """
        Test set_node method.
        """
        test_model = DataModel(nodes=self.good_nodes, relationships=self.good_relationships)

        new_node_label = "NewNode"
        new_node = test_model.set_node(new_node_label, csv_name="new_nodes.csv")
        self.assertIsNotNone(new_node)
        self.assertEqual(new_node.label, new_node_label)
        self.assertIn(new_node, test_model.nodes)

        updated_node = test_model.set_node("Person", csv_name="people.csv")
        self.assertEqual(updated_node.csv_name, "people.csv")

        with self.assertRaises(ValueError):
            test_model.set_node("Person", invalid_attr="value")

    def test_set_relationship(self) -> None:
        """
        Test set_relationship method.
        """
        # Ensure nodes are correctly initialized
        test_model = DataModel(nodes=self.good_nodes, relationships=self.good_relationships)
        print("Nodes in test_model:", [node.label for node in test_model.nodes])

        source_node_label = "Individual"
        target_node_label = "Address"

        assert test_model.get_node(source_node_label) is not None, "Source node does not exist"

        # Adding a new relationship
        new_relationship_type = "NEW_REL"
        new_relationship = test_model.set_relationship(
            new_relationship_type, source_node_label, target_node_label, csv_name="relationships.csv"
        )
        self.assertIsNotNone(new_relationship)
        self.assertEqual(new_relationship.type, new_relationship_type)
        self.assertEqual(new_relationship.source, source_node_label)
        self.assertEqual(new_relationship.target, target_node_label)
        self.assertIn(new_relationship, test_model.relationships)

        # Updating an existing relationship
        updated_relationship = test_model.set_relationship(
            "HAS_ADDRESS", source_node_label, target_node_label, csv_name="addresses.csv"
        )
        self.assertEqual(updated_relationship.csv_name, "addresses.csv")

        # Invalid attribute (should raise ValueError)
        with self.assertRaises(ValueError):
            test_model.set_relationship("FRIENDS_WITH", source_node_label, target_node_label, invalid_attr="value")

        # Non-existing source node (should raise ValueError)
        with self.assertRaises(ValueError):
            test_model.set_relationship("NEW_REL", "NonExistingNode", target_node_label)

        # Non-existing target node (should raise ValueError)
        with self.assertRaises(ValueError):
            test_model.set_relationship("NEW_REL", source_node_label, "NonExistingNode")

    def test_mutate_node(self) -> None:
        """
        Test mutate_node method.
        """
        test_model = DataModel(nodes=self.good_nodes, relationships=self.good_relationships)

        current_label = "Person"
        mutated_node = test_model.mutate_node(current_label, label="Individual")
        self.assertEqual(mutated_node.label, "Individual")

        self.assertIsNotNone(test_model.get_node("Individual"))
        self.assertIsNone(test_model.get_node(current_label))

        with self.assertRaises(ValueError):
            test_model.mutate_node("NonExistingNode", label="NewLabel")

        with self.assertRaises(ValueError):
            test_model.mutate_node("Person", invalid_attr="value")

    def test_mutate_relationship(self) -> None:
        """
        Test mutate_relationship method.
        """
        test_model = DataModel(nodes=self.good_nodes, relationships=self.good_relationships)

        current_type = "HAS_ADDRESS"
        mutated_relationship = test_model.mutate_relationship(current_type, type="HAS_NEW_ADDRESS")
        self.assertEqual(mutated_relationship.type, "HAS_NEW_ADDRESS")

        self.assertIsNotNone(test_model.get_relationship("HAS_NEW_ADDRESS"))
        self.assertIsNone(test_model.get_relationship(current_type))

        with self.assertRaises(ValueError):
            test_model.mutate_relationship("NON_EXISTING_REL", type="NEW_TYPE")

        with self.assertRaises(ValueError):
            test_model.mutate_relationship("FRIENDS_WITH", invalid_attr="value")

    def test_add_node(self):
        """
        Test adding a new node to the data model.
        """
        test_model = DataModel(nodes=self.good_nodes, relationships=self.good_relationships)
        print("Nodes in test_model:", [node.label for node in test_model.nodes])

        pet_name = Property(name="name", type="str", csv_mapping="pet_name", is_unique=True)
        pet_kind = Property(name="kind", type="str", csv_mapping="pet_kind", is_unique=False)
        pet_node = Node(label="LEGEND", properties=[pet_name, pet_kind])

        test_model.add_node(pet_node)
        self.assertIn(pet_node, test_model.nodes)

        with self.assertRaises(ValueError):
            test_model.add_node(pet_node)


if __name__ == "__main__":
    unittest.main()
