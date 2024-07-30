from typing import List, Dict, Union

from pydantic import BaseModel, field_validator

from ..arrows import ArrowsNode
from .property import Property
from ..solutions_workbench import SolutionsWorkbenchNode


class Node(BaseModel):
    """
    Standard Node representation.
    """

    label: str
    properties: List[Property]
    csv_name: str = ""

    def __init__(
        self, label: str, properties: List[Property] = [], csv_name: str = ""
    ) -> None:
        super().__init__(label=label, properties=properties, csv_name=csv_name)
        """
        Standard Node representation.

        Attributes
        -------
        label : str
            The node label.
        properties : List[Property]
            A list of the properties within the node.
        csv_name : str, optional
            The name of the CSV containing the node's information, by default = ""
        """

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
        The node property names.

        Returns
        -------
        List[str]
            A list of the property names in the node.
        """

        return [prop.name for prop in self.properties]

    @property
    def property_column_mapping(self) -> Dict[str, Union[str, List[str]]]:
        """
        A map of property names to their respective CSV columns.

        Returns
        -------
        Dict[str, str | List[str]]
            A dictionary with property name keys and CSV column values.
        """

        return {prop.name: prop.csv_mapping for prop in self.properties}

    @property
    def unique_properties(self) -> List[Property]:
        """
        The node's unique properties.

        Returns
        -------
        List[str]
            A list of unique properties.
        """

        return [prop for prop in self.properties if prop.is_unique]

    @property
    def unique_properties_column_mapping(self) -> Dict[str, Union[str, List[str]]]:
        """
        Map of unique properties to their respective CSV columns.

        Returns
        -------
        Dict[str, str | List[str]]
            A dictionary with unique property name keys and CSV column values.
        """

        return {
            prop.name: prop.csv_mapping for prop in self.properties if prop.is_unique
        }

    @property
    def nonunique_properties(self) -> List[Property]:
        """
        The node's nonunique properties.

        Returns
        -------
        List[str]
            A list of nonunique properties.
        """

        return [prop for prop in self.properties if not prop.is_unique]

    @property
    def nonunique_properties_column_mapping(self) -> Dict[str, str]:
        """
        Map of nonunique properties to their respective CSV columns.

        Returns
        -------
        Dict[str, str | List[str]]
            A dictionary with nonunique property name keys and CSV column values.
        """

        return {
            prop.name: prop.csv_mapping
            for prop in self.properties
            if not prop.is_unique
        }

    @property
    def node_keys(self) -> List[Property]:
        """
        The node key properties, if any.

        Returns
        -------
        List[Property]
            A list of the properties that make up a node key, if any.
        """

        return [prop for prop in self.properties if prop.part_of_key]

    @property
    def node_key_mapping(self) -> Dict[str, str]:
        """
        Map of node keys to their respective csv columns.

        Returns
        -------
        Dict[str, str]
            A dictionary with node key property keys and CSV column values.
        """

        return {
            prop.name: prop.csv_mapping for prop in self.properties if prop.part_of_key
        }

    @property
    def nonunique_properties_mapping_for_set_clause(self) -> Dict[str, str]:
        """
        Map of nonunique properties to their respective csv columns if a property is not unique or a node key.

        Returns
        -------
        Dict[str, str]
            A dictionary of nonunique or non node key property keys and CSV column values.
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
            A list with unique or node key property keys and CSV column values.
        """

        return [
            prop
            for prop in self.properties
            if not prop.is_unique and not prop.part_of_key
        ]

    def validate_properties(self, csv_columns: List[str]) -> List[Union[str, None]]:
        errors = []

        for prop in self.properties:
            if prop.csv_mapping not in csv_columns:
                errors.append(
                    f"The node {self.label} has the property {prop.name} mapped to csv column {prop.csv_mapping} which does not exist. {prop} should be edited or removed from node {self.label}."
                )
            if prop.is_unique and prop.part_of_key:
                errors.append(
                    f"The node {self.label} has the property {prop.name} identified as unique and a node key. Assume uniqueness and set part_of_key to False."
                )

        if len(self.node_keys) == 1:
            errors.append(
                f"The node {self.label} has a node key on only one property {self.node_keys[0].name}. Node keys must exist on two or more properties."
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
    def from_arrows(cls, arrows_node: ArrowsNode) -> "Node":
        """
        Initialize a Node from an arrows node.
        """

        props = [
            Property.from_arrows(arrows_property={k: v})
            for k, v in arrows_node.properties.items()
            if k != "csv" and not v.lower().rstrip().endswith("ignore")
        ]

        csv_name = (
            arrows_node.properties["csv"]
            if "csv" in arrows_node.properties.keys()
            else arrows_node.caption
        )

        # support only single labels for now, take first label
        return cls(label=arrows_node.labels[0], properties=props, csv_name=csv_name)

    def to_solutions_workbench(
        self, key: str, x: int, y: int
    ) -> "SolutionsWorkbenchNode":
        """
        Return a Solutions Workbench compatible Node.
        """

        props = {prop.name: prop.to_solutions_workbench() for prop in self.properties}

        return SolutionsWorkbenchNode(
            key=key,
            label=self.label,
            properties=props,
            x=x,
            y=y,
            description=self.csv_name,
        )

    @classmethod
    def from_solutions_workbench(
        cls, solutions_workbench_node: SolutionsWorkbenchNode
    ) -> "Node":
        """
        Initialize a core Node from a Solutions Workbench Node.
        """

        props = [
            Property.from_solutions_workbench(solutions_workbench_property=prop)
            for prop in solutions_workbench_node.properties.values()
        ]

        csv_name = solutions_workbench_node.description

        # support only single labels for now, take first label
        return cls(
            label=solutions_workbench_node.label, properties=props, csv_name=csv_name
        )
