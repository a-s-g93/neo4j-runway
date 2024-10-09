from typing import Dict, List, Optional, Union

from pydantic import (
    BaseModel,
    ValidationError,
    ValidationInfo,
    field_validator,
    model_validator,
)
from pydantic_core import InitErrorDetails, PydanticCustomError

from ...exceptions import (
    InvalidColumnMappingError,
    InvalidSourceNameError,
    NonuniqueNodeError,
)
from ..arrows import ArrowsNode
from ..solutions_workbench import SolutionsWorkbenchNode
from .property import Property


class Node(BaseModel):
    """
    Standard Node representation.

    Attributes
    -------
    label : str
        The node label.
    properties : List[Property]
        A list of the properties within the node.
    source_name : str, optional
        The name of the file containing the node's information.
    """

    label: str
    properties: List[Property]
    source_name: str = "file"

    # def __init__(
    #     self, label: str, properties: List[Property] = list(), source_name: str = "file"
    # ) -> None:
    #     super().__init__(label=label, properties=properties, source_name=source_name)
    #     """
    #     Standard Node representation.

    #     Parameters
    #     ----------
    #     label : str
    #         The node label.
    #     properties : List[Property]
    #         A list of the properties within the node.
    #     source_name : str, optional
    #         The name of the file containing the node's information, by default = "file"
    #     """

    # @field_validator("source_name")
    # def validate_source_name(cls, v: str) -> str:
    #     """
    #     Validate the CSV name provided.
    #     """

    #     if v == "file":
    #         return v
    #     else:
    #         if not v.endswith(".csv"):
    #             return v + ".csv"
    #     return v

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

        return {prop.name: prop.column_mapping for prop in self.properties}

    @property
    def unique_properties(self) -> List[Property]:
        """
        The node's unique properties.

        Returns
        -------
        List[Property]
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
            prop.name: prop.column_mapping for prop in self.properties if prop.is_unique
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
            prop.name: prop.column_mapping
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
            prop.name: prop.column_mapping
            for prop in self.properties
            if prop.part_of_key
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
            A list with unique or node key property keys and CSV column values.
        """

        return [
            prop
            for prop in self.properties
            if not prop.is_unique and not prop.part_of_key
        ]

    @property
    def node_key_aliases(self) -> List[Property]:
        """
        List of node key aliases, if they exist.

        Returns
        -------
        List[Property]
            The aliases.
        """

        return [p for p in self.properties if p.part_of_key and p.alias is not None]

    @property
    def unique_property_aliases(self) -> List[Property]:
        """
        List of unique property aliases, if they exist.

        Returns
        -------
        List[Property]
            The aliases.
        """

        return [p for p in self.properties if p.is_unique and p.alias is not None]

    @field_validator("source_name")
    @classmethod
    def validate_source_name(cls, source_name: str, info: ValidationInfo) -> str:
        sources: List[str] = (
            list(info.context.get("valid_columns", dict()).keys())
            if info.context is not None
            else list()
        )

        # skip for single file input
        if len(sources) == 1:
            return sources[0]
        elif source_name in sources:
            return source_name
        else:
            raise InvalidSourceNameError(
                f"{source_name} is not in the provided file list: {sources}."
            )

    @model_validator(mode="after")
    def validate_property_mappings(self, info: ValidationInfo) -> "Node":
        valid_columns: Dict[str, List[str]] = (
            info.context.get("valid_columns") if info.context is not None else dict()
        )
        errors: List[InitErrorDetails] = list()
        for prop in self.properties:
            if prop.column_mapping not in valid_columns.get(self.source_name, list()):
                errors.append(
                    InitErrorDetails(
                        type=PydanticCustomError(
                            "invalid_column_mapping_error",
                            f"The `Node` {self.label} has the `Property` {prop.name} mapped to column {prop.column_mapping} which is not allowed for source file {self.source_name}. Removed {prop.name} from `Node` {self.label}.",
                        ),
                        loc=("properties",),
                        input=self.properties,
                        ctx={},
                    )
                )

        if errors:
            raise ValidationError.from_exception_data(
                title=self.__class__.__name__,
                line_errors=errors,
            )

        return self

    @model_validator(mode="after")
    def enforce_uniqueness(self, info: ValidationInfo) -> "Node":
        enforce_uniqueness: bool = (
            info.context.get("enforce_uniqueness") if info.context is not None else True
        )
        if enforce_uniqueness:
            if len(self.unique_properties) == 0 and len(self.node_keys) < 2:
                # keep it simple by asking only for a unique property, not to create a node key combo
                raise NonuniqueNodeError(
                    f"The node {self.label} must contain a unique `Property` in `properties`."
                )
        return self

    def to_arrows(self, x_position: float, y_position: float) -> ArrowsNode:
        """
        Return an arrows.app compatible node.
        """
        pos = {"x": x_position, "y": y_position}
        props = {
            x.name: x.column_mapping
            + " | "
            + x.type
            + (" | unique" if x.is_unique else "")
            + (" | nodekey" if x.part_of_key else "")
            for x in self.properties
        }

        return ArrowsNode(
            id=self.label,
            caption=self.source_name,
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

        source_name = (
            arrows_node.properties["csv"]
            if "csv" in arrows_node.properties.keys()
            else arrows_node.caption
        )

        # support only single labels for now, take first label
        return cls(
            label=arrows_node.labels[0], properties=props, source_name=source_name
        )

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
            description=self.source_name,
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

        source_name = solutions_workbench_node.description

        # support only single labels for now, take first label
        return cls(
            label=solutions_workbench_node.label,
            properties=props,
            source_name=source_name,
        )
