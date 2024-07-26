from typing import Dict, Optional

from pydantic import BaseModel, field_validator

from ..solutions_workbench import SolutionsWorkbenchProperty
from ...resources.mappings import (
    TYPES_MAP_NEO4J_TO_PYTHON,
    TYPES_MAP_PYTHON_TO_NEO4J,
    TYPES_MAP_SOLUTIONS_WORKBENCH_TO_PYTHON,
    TYPES_MAP_PYTHON_TO_SOLUTIONS_WORKBENCH,
)


class Property(BaseModel):
    """
    Property representation.
    """

    name: str
    type: str
    csv_mapping: str
    csv_mapping_other: Optional[str] = None
    is_unique: bool = False
    part_of_key: bool = False
    # is_indexed: bool
    # must_exist: bool

    @field_validator("type")
    def validate_type(cls, v: str):
        if v.lower() == "object" or v.lower() == "string":
            return "str"
        elif "float" in v.lower():
            return "float"
        elif v.lower().startswith("int"):
            return "int"
        elif "bool" in v.lower():
            return "bool"

        if v in list(TYPES_MAP_SOLUTIONS_WORKBENCH_TO_PYTHON.keys()):
            return TYPES_MAP_SOLUTIONS_WORKBENCH_TO_PYTHON[v]
        elif v in list(TYPES_MAP_NEO4J_TO_PYTHON.keys()):
            return TYPES_MAP_NEO4J_TO_PYTHON[v]
        elif v in list(TYPES_MAP_SOLUTIONS_WORKBENCH_TO_PYTHON.values()):
            return v
        elif v in list(TYPES_MAP_NEO4J_TO_PYTHON.values()):
            return v
        else:
            raise ValueError(f"Invalid Property type given: {v}")

    @property
    def neo4j_type(self) -> str:
        """
        The Neo4j property type.
        """
        return TYPES_MAP_PYTHON_TO_NEO4J[self.type]

    @classmethod
    def from_arrows(
        cls, arrows_property: Dict[str, str], caption: str = ""
    ) -> "Property":
        """
        Parse the arrows property representation into a standard Property model.
        Arrow property values are formatted as <csv_mapping> | <python_type> | <unique, nodekey> | <ignore>.
        """

        if "|" in list(arrows_property.values())[0]:
            prop_props = [
                x.strip() for x in list(arrows_property.values())[0].split("|")
            ]
            if "," in prop_props[0]:
                csv_mapping, csv_mapping_other = [
                    x.strip() for x in prop_props[0].split(",")
                ]
            else:
                csv_mapping: str = prop_props[0]
                csv_mapping_other = None

            python_type = prop_props[1]
            is_unique = "unique" in prop_props
            node_key = "nodekey" in prop_props
        else:
            csv_mapping: str = list(arrows_property.values())[0]
            python_type = "unknown"
            csv_mapping_other = None
            is_unique = False
            node_key = False

        return cls(
            name=list(arrows_property.keys())[0],
            csv_mapping=csv_mapping,
            csv_mapping_other=csv_mapping_other,
            type=python_type,
            is_unique=is_unique,
            part_of_key=node_key,
        )

    @classmethod
    def from_solutions_workbench(
        cls, solutions_workbench_property: SolutionsWorkbenchProperty
    ) -> "Property":
        """
        Parse the Solutions Workbench property into the standard property representation.
        """

        if "," in solutions_workbench_property.referenceData:
            csv_mapping, csv_mapping_other = [
                x.strip() for x in solutions_workbench_property.referenceData.split(",")
            ]
        else:
            csv_mapping, csv_mapping_other = (
                solutions_workbench_property.referenceData,
                None,
            )

        return cls(
            name=solutions_workbench_property.name,
            csv_mapping=csv_mapping,
            csv_mapping_other=csv_mapping_other,
            type=TYPES_MAP_SOLUTIONS_WORKBENCH_TO_PYTHON[
                solutions_workbench_property.datatype
            ],
            is_unique=solutions_workbench_property.hasUniqueConstraint,
            part_of_key=solutions_workbench_property.isPartOfKey,
        )

    def to_solutions_workbench(self) -> "SolutionsWorkbenchProperty":
        """
        Parse into a Solutions Workbench property representation.
        """
        if self.csv_mapping_other:
            reference_data = f"{self.csv_mapping}, {self.csv_mapping_other}"
        else:
            reference_data = self.csv_mapping

        return SolutionsWorkbenchProperty(
            key=self.name,
            name=self.name,
            datatype=TYPES_MAP_PYTHON_TO_SOLUTIONS_WORKBENCH[self.type],
            referenceData=reference_data,
            isPartOfKey=self.part_of_key,
            isIndexed=self.is_unique,
            mustExist=self.part_of_key,
            hasUniqueConstraint=self.is_unique,
            isArray=True if self.type.startswith("List") else False,
        )
