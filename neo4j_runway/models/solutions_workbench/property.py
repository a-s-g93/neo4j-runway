"""
This file contains a property as it is represented in Solutions Workbench.
"""

from typing import List, Optional

from pydantic import BaseModel, field_validator
from ...resources.mappings import TYPES_MAP_SOLUTIONS_WORKBENCH_TO_PYTHON


class SolutionsWorkbenchProperty(BaseModel):
    """
    Property representation in Solutions Workbench.
    """

    key: str
    name: str
    datatype: str
    referenceData: str
    description: Optional[str] = None
    fromDataSources: List[str] = list()
    isPartOfKey: bool
    isArray: bool
    isIndexed: bool
    mustExist: bool
    hasUniqueConstraint: bool

    @field_validator("datatype")
    def validate_type(cls, v: str) -> str:
        if v not in set(TYPES_MAP_SOLUTIONS_WORKBENCH_TO_PYTHON.keys()):
            raise ValueError(
                f"Invalid type provided to SolutionsWorkbenchProperty cosntructor: {v}"
            )
        return v
