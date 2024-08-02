import unittest

from neo4j_runway.models import Property, Relationship
from neo4j_runway.models.solutions_workbench import (
    SolutionsWorkbenchRelationship,
)


class TestSolutionsWorkbenchRelationship(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.json_input = {
            "classType": "RelationshipType",
            "key": "Rel2",
            "type": "HAS_PET",
            "startNodeLabelKey": "Node0",
            "endNodeLabelKey": "Node2",
            "properties": {
                "Prop8": {
                    "key": "Prop8",
                    "name": "city",
                    "datatype": "String",
                    "referenceData": "city",
                    "description": None,
                    "fromDataSources": [],
                    "isPartOfKey": True,
                    "isArray": False,
                    "isIndexed": True,
                    "mustExist": True,
                    "hasUniqueConstraint": True,
                }
            },
            "referenceData": {},
            "description": "pets-2.csv",
            "outMinCardinality": "0",
            "outMaxCardinality": "many",
            "inMinCardinality": "0",
            "inMaxCardinality": "many",
            "display": {
                "color": "black",
                "fontSize": 14,
                "strokeWidth": 3,
                "offset": 0,
                "glyph": None,
            },
        }

    def test_init_from_json(self) -> None:
        sw_rel = SolutionsWorkbenchRelationship(**self.json_input)

        self.assertEqual(len(sw_rel.__dict__.keys()), len(self.json_input.keys()))

        test_keys = [
            "key",
            "type",
            "startNodeLabelKey",
            "endNodeLabelKey",
            "description",
            "referenceData",
            "outMinCardinality",
            "outMaxCardinality",
            "inMinCardinality",
            "inMaxCardinality",
        ]

        for k in test_keys:
            self.assertEqual(self.json_input[k], sw_rel.__dict__[k])

    def test_init_from_core_relationship(self) -> None:
        city = Property(
            name="city",
            type="str",
            csv_mapping="city",
            is_unique=True,
            part_of_key=True,
        )

        core_rel = Relationship(
            type="HAS_PET",
            source="N0de2",
            target="Node2",
            properties=[city],
            csv_name="pets-2.csv",
        )

        sw_rel: SolutionsWorkbenchRelationship = core_rel.to_solutions_workbench(
            key="rel0"
        )

        self.assertEqual("rel0", sw_rel.key)
        self.assertEqual(core_rel.type, sw_rel.type)
        self.assertEqual(core_rel.property_names, list(sw_rel.properties.keys()))
        self.assertEqual(core_rel.csv_name, sw_rel.description)

    def test_init_to_core_relationship(self) -> None:
        sw_rel = SolutionsWorkbenchRelationship(**self.json_input)
        node_id_to_label_map = {"Node0": "Person", "Node2": "Pet"}
        core_rel = Relationship.from_solutions_workbench(
            solutions_workbench_relationship=sw_rel,
            node_id_to_label_map=node_id_to_label_map,
        )

        self.assertEqual(core_rel.type, sw_rel.type)
        self.assertEqual(len(core_rel.properties), len(sw_rel.properties.keys()))
        self.assertEqual(core_rel.csv_name, sw_rel.description)
        self.assertEqual(
            core_rel.source, node_id_to_label_map[sw_rel.startNodeLabelKey]
        )
        self.assertEqual(core_rel.target, node_id_to_label_map[sw_rel.endNodeLabelKey])
