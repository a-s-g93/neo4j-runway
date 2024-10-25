from typing import Dict, List

from pydantic import (
    BaseModel,
    ValidationError,
    ValidationInfo,
    field_validator,
    model_validator,
)
from pydantic_core import InitErrorDetails, PydanticCustomError

from ...exceptions import InvalidSourceNameError
from ...utils.naming_conventions import fix_node_label, fix_relationship_type
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

    def __str__(self) -> str:
        return f"(:{self.source})-[:{self.type}]->(:{self.target})"

    def get_schema(self, verbose: bool = True, neo4j_typing: bool = False) -> str:
        """
        Get the Relationship schema.

        Parameters
        ----------
        verbose : bool, optional
            Whether to provide more detail, by default True
        neo4j_typing : bool, optional
            Whether to use Neo4j types instead of Python types, by default False

        Returns
        -------
        str
            The schema
        """

        props = ""
        for p in self.properties:
            props += (
                "* " + p.get_schema(verbose=verbose, neo4j_typing=neo4j_typing) + "\n"
            )
        schema = f"""(:{self.source})-[:{self.type}]->(:{self.target})
{props}"""

        return schema

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

    @field_validator("type")
    def validate_type_naming(cls, t: str, info: ValidationInfo) -> str:
        apply_neo4j_naming_conventions: bool = (
            info.context.get("apply_neo4j_naming_conventions", True)
            if info.context is not None
            else True
        )

        if apply_neo4j_naming_conventions:
            return fix_relationship_type(t)

        return t

    @field_validator("source")
    def validate_source_naming(cls, source: str, info: ValidationInfo) -> str:
        apply_neo4j_naming_conventions: bool = (
            info.context.get("apply_neo4j_naming_conventions", True)
            if info.context is not None
            else True
        )

        if apply_neo4j_naming_conventions:
            return fix_node_label(source)

        return source

    @field_validator("target")
    def validate_type(cls, target: str, info: ValidationInfo) -> str:
        apply_neo4j_naming_conventions: bool = (
            info.context.get("apply_neo4j_naming_conventions", True)
            if info.context is not None
            else True
        )

        if apply_neo4j_naming_conventions:
            return fix_node_label(target)

        return target

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
        elif source_name in sources or not sources:
            return source_name
        else:
            raise InvalidSourceNameError(
                f"{source_name} is not in the provided file list: {sources}."
            )

    @model_validator(mode="after")
    def validate_property_mappings(self, info: ValidationInfo) -> "Relationship":
        valid_columns: Dict[str, List[str]] = (
            info.context.get("valid_columns", {}) if info.context is not None else {}
        )
        errors: List[InitErrorDetails] = list()

        if valid_columns:
            for prop in self.properties:
                if prop.column_mapping not in valid_columns.get(
                    self.source_name, list()
                ):
                    errors.append(
                        InitErrorDetails(
                            type=PydanticCustomError(
                                "invalid_column_mapping_error",
                                f"The `Relationship` {self.type} has the `Property` {prop.name} mapped to column {prop.column_mapping} which is not allowed for source file {self.source_name}. Removed {prop.name} from `Relationship` {self.type}.",
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
