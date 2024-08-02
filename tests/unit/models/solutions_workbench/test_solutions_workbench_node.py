import unittest

from neo4j_runway.models import Node, Property
from neo4j_runway.models.solutions_workbench import SolutionsWorkbenchNode


class TestSolutionsWorkbenchNode(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.json_input = {
            "classType": "NodeLabel",
            "label": "Pet",
            "fromDataSources": [],
            "key": "Node2",
            "indexes": [],
            "properties": {
                "Prop3": {
                    "key": "Prop3",
                    "name": "name",
                    "datatype": "String",
                    "referenceData": "pet_name",
                    "description": None,
                    "fromDataSources": [],
                    "isPartOfKey": False,
                    "isArray": False,
                    "isIndexed": True,
                    "mustExist": False,
                    "hasUniqueConstraint": True,
                },
                "Prop4": {
                    "key": "Prop4",
                    "name": "kind",
                    "datatype": "String",
                    "referenceData": "pet",
                    "description": None,
                    "fromDataSources": [],
                    "isPartOfKey": False,
                    "isArray": False,
                    "isIndexed": False,
                    "mustExist": False,
                    "hasUniqueConstraint": False,
                },
            },
            "secondaryNodeLabelKeys": [],
            "isOnlySecondaryNodeLabel": False,
            "description": "pets-2.csv",
            "referenceData": '{"secondaryNodeLabelKeys":[],"isOnlySecondaryNodeLabel":False}',
            "display": {
                "color": "white",
                "stroke": "black",
                "strokeWidth": 4,
                "x": 540,
                "y": 120,
                "radius": 40,
                "size": "md",
                "width": 80,
                "height": 80,
                "fontSize": 14,
                "fontColor": "black",
                "textLocation": "middle",
                "isLocked": False,
                "glyphs": [],
            },
            "x": 540,
            "y": 120,
            "hasAnnotation": True,
        }

    def test_init_from_json(self) -> None:
        sw_node = SolutionsWorkbenchNode(**self.json_input)

        self.assertEqual(len(sw_node.model_dump().keys()), len(self.json_input.keys()))

        test_keys = [
            "label",
            "fromDataSources",
            "secondaryNodeLabelKeys",
            "isOnlySecondaryNodeLabel",
            "description",
            "referenceData",
            "hasAnnotation",
        ]

        for k in test_keys:
            self.assertEqual(self.json_input[k], sw_node.__dict__[k])

    def test_init_from_core_node(self) -> None:
        name = Property(
            name="name",
            type="str",
            csv_mapping="pet_name",
            is_unique=True,
            part_of_key=False,
        )
        kind = Property(
            name="kind",
            type="str",
            csv_mapping="pet",
            is_unique=False,
            part_of_key=False,
        )

        core_node = Node(label="Pet", csv_name="pets-2.csv", properties=[name, kind])

        sw_node = core_node.to_solutions_workbench(key="node0", x=50, y=0)

        self.assertEqual(core_node.label, sw_node.label)
        self.assertEqual(core_node.property_names, list(sw_node.properties.keys()))
        self.assertEqual(core_node.csv_name, sw_node.description)
        self.assertEqual("node0", sw_node.key)

    def test_init_to_core_node(self) -> None:
        sw_node = SolutionsWorkbenchNode(**self.json_input)

        core_node = Node.from_solutions_workbench(solutions_workbench_node=sw_node)

        self.assertEqual(core_node.label, sw_node.label)
        self.assertEqual(len(core_node.properties), len(sw_node.properties.keys()))
        self.assertEqual(core_node.csv_name, sw_node.description)
