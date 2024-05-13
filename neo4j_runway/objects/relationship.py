from typing import List, Dict, Union, Any, Self

from pydantic import BaseModel

from ..objects.node import Node
from ..objects.property import Property
from ..objects.arrows import ArrowsRelationship


class Relationship(BaseModel):
    """
    Relationship representation.
    """

    type: str
    properties: List[Property] = []
    source: str
    target: str
    csv_name: str = ""

    def __init__(
        self,
        type: str,
        source: str,
        target: str,
        properties: List[Property] = [],
        csv_name: str = "",
    ) -> None:
        super().__init__(
            type=type,
            source=source,
            target=target,
            properties=properties,
            csv_name=csv_name,
        )

        if self.properties is None:
            self.properties = []

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

        return {prop.name: prop.csv_mapping for prop in self.properties}

    @property
    def unique_properties(self) -> List[str]:
        """
        The relationship's unique properties.
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

    def validate_properties(self, csv_columns: List[str]) -> List[Union[str, None]]:
        errors = []
        if self.properties is not None:
            for prop in self.properties:
                if prop.csv_mapping not in csv_columns:
                    # raise ValueError(
                    errors.append(
                        f"The relationship {self.type} the property {prop.name} mapped to csv column {prop.csv_mapping} which does not exist. {prop} should be edited or removed from relationship {self.type}."
                    )
                    # )
        return errors

    def to_arrows(self) -> ArrowsRelationship:
        """
        Return an arrows.app compatible relationship.
        """

        props = {
            x.name: x.csv_mapping + " | " + x.type + " | unique" if x.is_unique else ""
            for x in self.properties
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
        cls, arrows_relationship: ArrowsRelationship, node_id_label_map: Dict[str, str]
    ) -> Self:
        """
        Initialize a relationship from an arrows relationship.
        """

        props = [
            Property.from_arrows(arrows_property={k: v})
            for k, v in arrows_relationship.properties.items() if k != "csv"
        ]

        csv_name = arrows_relationship.properties["csv"]
        # csv_name = _get_relationship_csv_name(
        #     source=node_id_label_map[arrows_relationship.fromId],
        #     target=node_id_label_map[arrows_relationship.toId],
        #     nodes_dict=node_id_label_map,
        # )
        return cls(
            type=arrows_relationship.type,
            source=node_id_label_map[arrows_relationship.fromId],
            target=node_id_label_map[arrows_relationship.toId],
            properties=props,
            csv_name=csv_name,
        )


def _get_relationship_csv_name(
    source: str, target: str, nodes_dict: Dict[str, Node]
) -> str:
    """
    Find the csv name for a Relationship according to the source and target csv names.
    """

    source_csv = ""
    target_csv = ""

    for label, node in nodes_dict.items():
        if label == source:
            source_csv = node.csv_name
        if label == target:
            target_csv = node.csv_name

    return source_csv if source_csv == target_csv else ""
