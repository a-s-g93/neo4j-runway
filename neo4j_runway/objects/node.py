from typing import List, Dict, Union, Any, Self

from pydantic import BaseModel, field_validator

from ..objects.arrows import ArrowsNode
from ..objects.property import Property


class Node(BaseModel):
    """
    Node representation.
    """

    label: str
    properties: List[Property] = []
    csv_name: str = ""

    def __init__(
        self, label: str, properties: List[Property] = [], csv_name: str = ""
    ) -> None:
        super().__init__(label=label, properties=properties, csv_name=csv_name)

    @field_validator("csv_name")
    def validate_csv_name(cls, v: str) -> str:
        """
        Validate the CSV name provided.
        """

        if v == "":
            return v
        else:
            if not v.endswith(".csv"):
                return v + ".csv"
        return v

    @property
    def property_names(self) -> List[str]:
        """
        The node's property names.
        """

        return [prop.name for prop in self.properties]

    @property
    def property_column_mapping(self) -> Dict[str, str]:
        """
        Map of properties to their respective csv columns.
        """

        return {prop.name: prop.csv_mapping for prop in self.properties}

    @property
    def unique_properties(self) -> List[str]:
        """
        The node's unique properties.
        """

        return [prop.name for prop in self.properties if prop.is_unique]

    @property
    def unique_properties_column_mapping(self) -> Dict[str, str]:
        """
        Map of unique properties to their respective csv columns.
        """

        return {
            prop.name: prop.csv_mapping for prop in self.properties if prop.is_unique
        }

    @property
    def nonunique_properties(self) -> List[str]:
        """
        The node's nonunique properties.
        """

        return [prop.name for prop in self.properties if not prop.is_unique]

    @property
    def nonunique_properties_column_mapping(self) -> Dict[str, str]:
        """
        Map of nonunique properties to their respective csv columns.
        """

        return {
            prop.name: prop.csv_mapping
            for prop in self.properties
            if not prop.is_unique
        }

    @property
    def node_keys(self) -> List[str]:
        """
        The node's keys.
        """

        return [prop.name for prop in self.properties if prop.part_of_key]

    @property
    def node_key_mapping(self) -> Dict[str, str]:
        """
        Map of node keys to their respective csv columns.
        """

        return {
            prop.name: prop.csv_mapping for prop in self.properties if prop.part_of_key
        }

    @property
    def nonunique_properties_mapping_for_set_clause(self) -> Dict[str, str]:
        """
        Map of nonunique properties to their respective csv columns if a property is not unique or a node key.
        """

        return {
            prop.name: prop.csv_mapping
            for prop in self.properties
            if not prop.is_unique and not prop.part_of_key
        }

    def validate_properties(self, csv_columns: List[str]) -> List[Union[str, None]]:
        errors = []
        if self.properties is not None:
            for prop in self.properties:
                if prop.csv_mapping not in csv_columns:
                    errors.append(
                        f"The node {self.label} has the property {prop.name} mapped to csv column {prop.csv_mapping} which does not exist. {prop} should be edited or removed from node {self.label}."
                    )
        return errors

    def to_arrows(self, x_position: float, y_position: float) -> ArrowsNode:
        """
        Return an arrows.app compatible node.
        """
        pos = {"x": x_position, "y": y_position}
        props = {
            x.name: x.csv_mapping
            + " | "
            + x.type
            + (" | unique" if x.is_unique else "")
            + (" | nodekey" if x.part_of_key else "")
            for x in self.properties
        }

        return ArrowsNode(
            id=self.label,
            caption=self.csv_name,
            position=pos,
            labels=[self.label],
            properties=props,
        )

    @classmethod
    def from_arrows(cls, arrows_node: ArrowsNode) -> Self:
        """
        Initialize a Node from an arrows node.
        """

        props = [
            Property.from_arrows(arrows_property={k: v})
            for k, v in arrows_node.properties.items()
            if k != "csv"
        ]

        csv_name = (
            arrows_node.properties["csv"]
            if "csv" in arrows_node.properties.keys()
            else arrows_node.caption
        )

        # support only single labels for now, take first label
        return cls(label=arrows_node.labels[0], properties=props, csv_name=csv_name)
