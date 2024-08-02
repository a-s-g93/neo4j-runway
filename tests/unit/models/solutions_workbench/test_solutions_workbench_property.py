import unittest

from neo4j_runway.models import Property
from neo4j_runway.models.solutions_workbench import SolutionsWorkbenchProperty


class TestSolutionsWorkbenchProperty(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.json_input = {
            "key": "Prop4",
            "name": "kind",
            "datatype": "String",
            "referenceData": "pet",
            "description": None,
            "fromDataSources": [],
            "isPartOfKey": False,
            "isArray": False,
            "isIndexed": True,
            "mustExist": False,
            "hasUniqueConstraint": True,
        }

    def test_init_from_json(self) -> None:
        prop = SolutionsWorkbenchProperty(**self.json_input)

        self.assertEqual(len(prop.__dict__.keys()), len(self.json_input.keys()))

        for k, v in prop.__dict__.items():
            self.assertEqual(self.json_input[k], v)

    def test_init_from_core_property(self) -> None:
        core_prop = Property(
            name="kind",
            type="str",
            csv_mapping="pet",
            csv_mapping_other=None,
            is_unique=True,
            part_of_key=False,
        )
        sw_prop = core_prop.to_solutions_workbench()

        self.assertEqual(core_prop.name, sw_prop.key)
        self.assertEqual(core_prop.name, sw_prop.name)
        self.assertEqual("String", sw_prop.datatype)
        self.assertEqual(core_prop.csv_mapping, sw_prop.referenceData)
        self.assertIsNone(sw_prop.description)
        self.assertEqual([], sw_prop.fromDataSources)
        self.assertFalse(sw_prop.isArray)
        self.assertEqual(core_prop.is_unique, sw_prop.isIndexed)
        self.assertEqual(core_prop.part_of_key, sw_prop.isPartOfKey)
        self.assertFalse(sw_prop.mustExist)
        self.assertEqual(core_prop.is_unique, sw_prop.hasUniqueConstraint)

    def test_init_from_core_property_of_type_list(self) -> None:
        core_prop = Property(
            name="kind",
            type="List[str]",
            csv_mapping="pet",
            csv_mapping_other=None,
            is_unique=True,
            part_of_key=False,
        )
        sw_prop = core_prop.to_solutions_workbench()

        self.assertEqual("String Array", sw_prop.datatype)

    def test_init_from_core_property_with_multi_mapping(self) -> None:
        core_prop = Property(
            name="kind",
            type="str",
            csv_mapping="pet",
            csv_mapping_other="pet2",
            is_unique=True,
            part_of_key=False,
        )
        sw_prop = core_prop.to_solutions_workbench()

        self.assertEqual("pet, pet2", sw_prop.referenceData)

    def test_init_to_core_property(self) -> None:
        sw_prop = SolutionsWorkbenchProperty(**self.json_input)

        core_prop = Property.from_solutions_workbench(
            solutions_workbench_property=sw_prop
        )

        self.assertEqual(core_prop.name, sw_prop.name)
        self.assertEqual("str", core_prop.type)
        self.assertEqual(core_prop.csv_mapping, sw_prop.referenceData)
        self.assertEqual(core_prop.is_unique, sw_prop.isIndexed)
        self.assertEqual(core_prop.part_of_key, sw_prop.isPartOfKey)
        self.assertEqual(core_prop.is_unique, sw_prop.hasUniqueConstraint)

    def test_init_to_core_property_with_multi_mapping(self) -> None:
        sw_prop = SolutionsWorkbenchProperty(**self.json_input)
        sw_prop.referenceData = "pet, pet2"
        core_prop = Property.from_solutions_workbench(
            solutions_workbench_property=sw_prop
        )

        self.assertEqual("pet", core_prop.csv_mapping)
        self.assertEqual("pet2", core_prop.csv_mapping_other)
