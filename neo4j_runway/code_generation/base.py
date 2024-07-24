"""
This file contains the base conde generator class. All code generation classes must inherit from this class.
"""

from abc import ABC
from typing import Dict, Any

import yaml

from .cypher import *
from ..models import DataModel


class folded_unicode(str):
    pass


class literal_unicode(str):
    pass


def folded_unicode_representer(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style=">")


def literal_unicode_representer(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")


yaml.add_representer(folded_unicode, folded_unicode_representer)
yaml.add_representer(literal_unicode, literal_unicode_representer)


class BaseCodeGenerator(ABC):
    """
    Base class for code generation.
    """

    def __init__(
        self,
        data_model: DataModel,
        file_directory: str = "./",
        file_output_directory: str = "./",
        csv_name: str = "",
        strict_typing: bool = True,
    ):
        """
        This is the base class for code generation. All code generation classes must inherit from this class.

        Attributes
        ----------
        data_model : DataModel
            The data model to base ingestion code on.
        file_directory : str, optional
            Where the files are located. By default = "./"
        file_output_directory : str, optional
            The location that generated files should be saved to, by default "./"
        csv_name : str, optional
            The name of the CSV file. If more than one CSV is used, this arg should not be provided.
            CSV file names should be included within the data model. By default = ""
        strict_typing : bool, optional
            Whether to use the types declared in the data model (True), or infer types during ingestion (False). By default True
        """

        self.data_model: DataModel = data_model
        self.file_dir = file_directory
        self.file_output_dir = file_output_directory
        self.csv_name = csv_name
        self.strict_typing = strict_typing

        self._constraints: Dict[str, str] = dict()
        self._cypher: Dict[str, Dict[str, Any]] = dict()

        self._generate_base_cypher(strict_typing=self.strict_typing)

    def _generate_base_cypher(
        self,
        strict_typing: bool = True,
    ):
        for node in self.data_model.nodes:
            if len(node.unique_properties_column_mapping) > 0:
                # unique constraints
                for unique_property in node.unique_properties:
                    self._constraints[
                        generate_constraints_key(
                            label_or_type=node.label, unique_property=unique_property
                        )
                    ] = generate_unique_constraint(
                        label_or_type=node.label, unique_property=unique_property
                    )
            # node keys
            if node.node_keys:
                self._constraints[
                    generate_constraints_key(
                        label_or_type=node.label, unique_property=node.node_keys
                    )
                ] = generate_node_key_constraint(
                    label=node.label, unique_properties=node.node_keys
                )

            # add to cypher map
            self._cypher[node.label] = {
                "cypher": literal_unicode(
                    generate_merge_node_clause_standard(
                        node=node, strict_typing=strict_typing
                    )
                ),
                "csv": f"$BASE/{self.file_dir}{node.csv_name if self.csv_name == '' else self.csv_name}",
            }

        ## get relationships
        for rel in self.data_model.relationships:
            if len(rel.unique_properties_column_mapping) > 0:
                # unique constraints
                for unique_property in rel.unique_properties:
                    self._constraints[
                        generate_constraints_key(
                            label_or_type=rel.type, unique_property=unique_property
                        )
                    ] = generate_unique_constraint(
                        label_or_type=rel.type, unique_property=unique_property
                    )

            # relationship keys
            if rel.relationship_keys:
                self._constraints[
                    generate_constraints_key(
                        label_or_type=node.label, unique_property=node.node_keys
                    )
                ] = generate_relationship_key_constraint(
                    type=rel.type, unique_properties=rel.relationship_keys
                )

            source = self.data_model.node_dict[rel.source]
            target = self.data_model.node_dict[rel.target]
            self._cypher[f"{rel.type}_{rel.source}_{rel.target}"] = {
                "cypher": literal_unicode(
                    generate_merge_relationship_clause_standard(
                        relationship=rel,
                        source_node=source,
                        target_node=target,
                        strict_typing=strict_typing,
                    )
                ),
                "csv": f"$BASE/{self.file_dir}{rel.csv_name if self.csv_name == '' else self.csv_name}",
            }
