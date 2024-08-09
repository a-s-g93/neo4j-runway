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
            prop.name: prop.csv_mapping for prop in self.properties if prop.is_unique
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
            prop.name: prop.csv_mapping
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

    def get_property(self, property_name: str) -> Optional[Property]:
        """
        Retrieve a property by its name from the relationship's properties.

        Parameters
        ----------
        property_name : str
            The name of the property to retrieve.

        Returns
        -------
        Optional[Property]
            The property with the specified name if it exists, otherwise None.
        """
        for prop in self.properties:
            if prop.name == property_name:
                return prop
        return None

    def set_property(self, name: str, type: str, **kwargs) -> Property:
        """
        Add a new property with the specified name and type to the relationship
        or update an existing property.

        Parameters
        ----------
        name : str
            The name of the property to be added or updated.
        type : str
            The type of the property to be added or updated.
        kwargs : dict
            Additional attributes to set on the property.

        Returns
        -------
        Property
            The newly created or updated property with the specified name.

        Raises
        ------
        ValueError
            If the property with the specified name already exists.
        """
        existing_property = next((prop for prop in self.properties if prop.name == name), None)

        if existing_property is not None:
            for key, value in kwargs.items():
                if hasattr(existing_property, key):
                    setattr(existing_property, key, value)
                else:
                    raise ValueError(f"Property has no attribute '{key}'.")
            existing_property.type = type
            return existing_property

        new_property = Property(name=name, type=type, **kwargs)
        self.properties.append(new_property)
        return new_property

    def validate_properties(self, csv_columns: List[str]) -> List[Optional[str]]:
        errors: List[Optional[str]] = []
        if self.properties is not None:
            for prop in self.properties:
                if prop.csv_mapping not in csv_columns:
                    errors.append(
                        f"The relationship {self.type} the property {prop.name} mapped to csv column {prop.csv_mapping} which does not exist. {prop} should be edited or removed from relationship {self.type}."
                    )
                if prop.is_unique and prop.part_of_key:
                    errors.append(
                        f"The relationship {self.type} has the property {prop.name} identified as unique and a relationship key. Assume uniqueness and set part_of_key to False."
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

    def add_property(self, new_property: Property) -> None:
        """
        Add a new property to the relationship's list of properties.

        Parameters
        ----------
        new_property : Property
            The new property to add to the relationship.

        Raises
        ------
        ValueError
            If a property with the same name already exists in the relationship.
        """
        # Check if a property with the same name already exists
        if self.get_property(new_property.name) is not None:
            raise ValueError(f"Property with name '{new_property.name}' already exists.")

        self.properties.append(new_property)

    def to_arrows(self) -> ArrowsRelationship:
        """
        Return an arrows.app compatible relationship.
        """

        props = {
            x.name: (
                x.csv_mapping + " | " + x.type + " | unique"
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

        csv_name = (
            arrows_relationship.properties["csv"]
            if "csv" in arrows_relationship.properties.keys()
            else ""
        )

        return cls(
            type=arrows_relationship.type,
            source=node_id_to_label_map[arrows_relationship.fromId],
            target=node_id_to_label_map[arrows_relationship.toId],
            properties=props,
            csv_name=csv_name,
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
            description=self.csv_name,
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
            csv_name=solutions_workbench_relationship.description,
            source=node_id_to_label_map[
                solutions_workbench_relationship.startNodeLabelKey
            ],
            target=node_id_to_label_map[
                solutions_workbench_relationship.endNodeLabelKey
            ],
        )

    def __eq__(self, other:object) -> bool:
        if not isinstance(other, Relationship):
            return False
        return (
            self.type == other.type and
            self.source == other.source and
            self.target == other.target and
            set(self.properties) == set(other.properties)
        )

    def __hash__(self) -> int:
        return hash((
            self.type,
            self.source,
            self.target,
            tuple(sorted(self.properties, key= lambda p: p.name))
        ))

    def __repr__(self) -> str:
        return (
            f"Relationship(type={self.type!r}, source={self.source!r}, "
            f"target={self.target!r}, properties={self.properties!r}, "
            f"csv_name={self.csv_name!r})"
        )

