from typing import List, Dict, Union, Any

from pydantic import BaseModel

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

    def __init__(self, *a, **kw) -> None:
        super().__init__(*a, **kw)

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

        props = {x.name: x.csv_mapping + " | " + x.type for x in self.properties}
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
    ):
        """
        Initialize a relationship from an arrows relationship.
        """

        props = [
            cls._parse_arrows_property(arrows_property={k: v})
            for k, v in arrows_relationship.properties.items()
        ]
        return cls(
            type=arrows_relationship.type,
            source=node_id_label_map[arrows_relationship.fromId],
            target=node_id_label_map[arrows_relationship.toId],
            properties=props,
        )

    def _parse_arrows_property(arrows_property: Dict[str, str]) -> Property:
        """
        Parse the arrows property representation into a standard Property model.
        Unique property names are unable to be identified and will default to False.
        Arrow property values are formatted as <csv_mapping> | <python_type>.
        """

        if "|" in list(arrows_property.values())[0]:
            csv_mapping, python_type = [
                x.strip() for x in list(arrows_property.values())[0].split("|")
            ]
        else:
            csv_mapping = list(arrows_property.values())[0]
            python_type = "unknown"

        is_unique = False

        return Property(
            name=list(arrows_property.keys())[0],
            csv_mapping=csv_mapping,
            type=python_type,
            is_unique=is_unique,
        )
