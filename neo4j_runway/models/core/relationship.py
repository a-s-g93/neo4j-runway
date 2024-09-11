from typing import Dict, List, Optional

from pydantic import BaseModel, field_validator

from ..arrows import ArrowsRelationship
from ..solutions_workbench import (
    SolutionsWorkbenchRelationship,
)
from .property import Property


class Relationship(BaseModel):
    """
    Relationship representation.
    """

    type: str
    properties: List[Property] = list()
    source: str
    target: str
    source_name: str = "file"

    def __init__(
        self,
        type: str,
        source: str,
        target: str,
        properties: List[Property] = [],
        source_name: str = "file",
    ) -> None:
        super().__init__(
            type=type,
            source=source,
            target=target,
            properties=properties,
            source_name=source_name,
        )

        if self.properties is None:
            self.properties = []

    # @field_validator("source_name")
    # def validate_source_name(cls, v: str) -> str:
    #     """
    #     Validate the CSV name provided.
    #     """

    #     if v == "":
    #         return v
    #     else:
    #         if not v.endswith(".csv"):
    #             return v + ".csv"
    #     return v

    @property
    def property_names(self) -> List[str]:
        """
        The relationship's property names.
        """

        return [prop.name for prop in self.properties]

    @property
    def property_column_mapping(self) -> Dict[str, str]:
        """
        Map of properties to their respective csv columns.
        """

        return {prop.name: prop.column_mapping for prop in self.properties}

    @property
    def unique_properties(self) -> List[Property]:
        """
        The relationship's unique properties.
        """

        return [prop for prop in self.properties if prop.is_unique]

    @property
    def unique_properties_column_mapping(self) -> Dict[str, str]:
        """
        Map of unique properties to their respective csv columns.
        """

        return {
            prop.name: prop.column_mapping for prop in self.properties if prop.is_unique
        }

    @property
    def nonunique_properties(self) -> List[Property]:
        """
        The node's nonunique properties.
        """

        return [prop for prop in self.properties if not prop.is_unique]

    @property
    def nonunique_properties_column_mapping(self) -> Dict[str, str]:
        """
        Map of nonunique properties to their respective csv columns.
        """

        return {
            prop.name: prop.column_mapping
            for prop in self.properties
            if not prop.is_unique
        }

    @property
    def relationship_keys(self) -> List[Property]:
        """
        The relationship's key properties, if any.
        """

        return [prop for prop in self.properties if prop.part_of_key]

    @property
    def relationship_key_mapping(self) -> Dict[str, str]:
        """
        Map of relationship keys to their respective csv columns.
        """

        return {
            prop.name: prop.column_mapping
            for prop in self.properties
            if prop.part_of_key
        }

    @property
    def nonunique_properties_mapping_for_set_clause(self) -> Dict[str, str]:
        """
        Map of nonunique properties to their respective csv columns if a property is not unique or a node key.
        """

        return {
            prop.name: prop.column_mapping
            for prop in self.properties
            if not prop.is_unique and not prop.part_of_key
        }

    @property
    def nonidentifying_properties(self) -> List[Property]:
        """
        List of nonidentifying properties.

        Returns
        -------
        List[Property]
            A list with unique or relationship key property keys and CSV column values.
        """

        return [
            prop
            for prop in self.properties
            if not prop.is_unique and not prop.part_of_key
        ]

    def validate_source_name(
        self, valid_columns: Dict[str, List[str]]
    ) -> List[Optional[str]]:
        # skip for single file input
        if len(valid_columns.keys()) == 1 or self.source_name in list(
            valid_columns.keys()
        ):
            return []
        else:
            return [
                f"Relationship {self.type} has source_name {self.source_name} which is not in the provided file list: {list(valid_columns.keys())}."
            ]

    def validate_properties(
        self, valid_columns: Dict[str, List[str]]
    ) -> List[Optional[str]]:
        errors: List[Optional[str]] = []
        if self.properties is not None:
            for prop in self.properties:
                if prop.column_mapping not in valid_columns.get(
                    self.source_name, list()
                ):
                    errors.append(
                        f"The relationship {self.type} the property {prop.name} mapped to column {prop.column_mapping} which is not allowed for source file {self.source_name}. {prop.name} Remove {prop.name} from relationship {self.type}."
                    )
                if prop.is_unique and prop.part_of_key:
                    errors.append(
                        f"The relationship {self.type} has the property {prop.name} identified as unique and a relationship key. Remove the relationship key identifier."
                    )

        if len(self.relationship_keys) == 1:
            # only write error if this node is NOT also labeled as unique
            if self.relationship_keys[0].name not in [
                prop.name for prop in self.unique_properties
            ]:
                errors.append(
                    f"The relationship {self.type} has a relationship key on only one property {self.relationship_keys[0].name}. Relationship keys must exist on two or more properties."
                )
        return errors

    def to_arrows(self) -> ArrowsRelationship:
        """
        Return an arrows.app compatible relationship.
        """

        props = {
            x.name: (
                x.column_mapping + " | " + x.type + " | unique"
                if x.is_unique
                else "" + " | nodekey"
                if x.is_unique
                else ""
            )
            for x in self.properties
            if x.name != "csv"
        }
        arrows_id = self.type + self.source + self.target
        return ArrowsRelationship(
            id=arrows_id,
            fromId=self.source,
            toId=self.target,
            type=self.type,
            properties=props,
        )

    @classmethod
    def from_arrows(
        cls,
        arrows_relationship: ArrowsRelationship,
        node_id_to_label_map: Dict[str, str],
    ) -> "Relationship":
        """
        Initialize a relationship from an arrows relationship.
        """

        props = [
            Property.from_arrows(arrows_property={k: v})
            for k, v in arrows_relationship.properties.items()
            if k != "csv"
        ]

        source_name = (
            arrows_relationship.properties["csv"]
            if "csv" in arrows_relationship.properties.keys()
            else ""
        )

        return cls(
            type=arrows_relationship.type,
            source=node_id_to_label_map[arrows_relationship.fromId],
            target=node_id_to_label_map[arrows_relationship.toId],
            properties=props,
            source_name=source_name,
        )

    def to_solutions_workbench(self, key: str) -> "SolutionsWorkbenchRelationship":
        """
        Returns a Solutions Workbench compatible Relationship.
        """

        props = {prop.name: prop.to_solutions_workbench() for prop in self.properties}

        return SolutionsWorkbenchRelationship(
            key=key,
            type=self.type,
            properties=props,
            description=self.source_name,
            startNodeLabelKey=self.source,
            endNodeLabelKey=self.target,
        )

    @classmethod
    def from_solutions_workbench(
        cls,
        solutions_workbench_relationship: SolutionsWorkbenchRelationship,
        node_id_to_label_map: Dict[str, str],
    ) -> "Relationship":
        """
        Initialize a core Relationship from a Solutions Workbench Relationship.
        """

        props = list()

        if solutions_workbench_relationship.properties is not None:
            props = [
                Property.from_solutions_workbench(solutions_workbench_property=prop)
                for prop in solutions_workbench_relationship.properties.values()
            ]

        # support only single labels for now, take first label
        return cls(
            type=solutions_workbench_relationship.type,
            properties=props,
            source_name=solutions_workbench_relationship.description,
            source=node_id_to_label_map[
                solutions_workbench_relationship.startNodeLabelKey
            ],
            target=node_id_to_label_map[
                solutions_workbench_relationship.endNodeLabelKey
            ],
        )
