import os
from typing import Dict, List, Any, Union

import yaml

from ..objects.data_model import DataModel
from ..objects import Node
from ..objects import Relationship

model_maps = []
nodes_map = {}
create_constraints = {}

missing_properties_err = []


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


def lowercase_first_letter(str):
    return str[0].lower() + str[1:]


class IngestionGenerator:

    def __init__(
        self,
        data_model: DataModel,
        csv_name: str = "",
        username: Union[str, None] = None,
        password: Union[str, None] = None,
        uri: Union[str, None] = None,
        database: Union[str, None] = None,
        csv_dir: str = "",
        file_output_dir: str = "",
    ):

        self.data_model: DataModel = data_model
        self.username: Union[str, None] = username
        self.password: Union[str, None] = password
        self.uri: Union[str, None] = uri
        self.database: Union[str, None] = database
        self.csv_name: str = csv_name
        self.csv_dir: str = csv_dir
        self.file_output_dir: str = file_output_dir
        self._config_files_list: Union[List[Dict[str, Any]], None] = []
        self._constraints: Dict[str, str] = {}
        self._cypher_map: Dict[str, Dict[str, Any]] = {}

    def _generate_base_information(self, method: str = "api", batch_size: int = 100):
        for node in self.data_model.nodes:
            if len(node.unique_properties_column_mapping) > 0:
                # unique constraints
                for unique_property in node.unique_properties:
                    self._constraints[
                        generate_constraints_key(
                            label_or_type=node.label, unique_property=unique_property
                        )
                    ] = generate_constraint(
                        label_or_type=node.label, unique_property=unique_property
                    )
            # node keys
            if node.node_keys:
                self._constraints[
                    generate_constraints_key(
                        label_or_type=node.label, unique_property=node.node_keys
                    )
                ] = generate_node_key_constraint(
                    label=node.label, unique_property=node.node_keys
                )

            # add to cypher map
            self._cypher_map[lowercase_first_letter(node.label)] = {
                "cypher": literal_unicode(
                    generate_merge_node_clause_standard(node=node)
                ),
                "cypher_loadcsv": literal_unicode(
                    generate_merge_node_load_csv_clause(
                        node=node,
                        csv_name=(
                            node.csv_name if self.csv_name == "" else self.csv_name
                        ),
                        method=method,
                        batch_size=batch_size,
                    )
                ),
                "csv": f"$BASE/{self.csv_dir}{node.csv_name if self.csv_name == '' else self.csv_name}",
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
                    ] = generate_constraint(
                        label_or_type=rel.type, unique_property=unique_property
                    )

            # relationship keys
            if rel.relationship_keys:
                self._constraints[
                    generate_constraints_key(
                        label_or_type=node.label, unique_property=node.node_keys
                    )
                ] = generate_relationship_key_constraint(
                    type=rel.type, unique_property=rel.relationship_keys
                )

            source = self.data_model.node_dict[rel.source]
            target = self.data_model.node_dict[rel.target]
            self._cypher_map[f"{rel.source}_{rel.target}"] = {
                "cypher": literal_unicode(
                    generate_merge_relationship_clause_standard(
                        relationship=rel, source_node=source, target_node=target
                    )
                ),
                "cypher_loadcsv": literal_unicode(
                    generate_merge_relationship_load_csv_clause(
                        relationship=rel,
                        source_node=source,
                        target_node=target,
                        csv_name=rel.csv_name if self.csv_name == "" else self.csv_name,
                        method=method,
                        batch_size=batch_size,
                    )
                ),
                "csv": f"$BASE/{self.csv_dir}{rel.csv_name if self.csv_name == '' else self.csv_name}",
            }

        self._config_files_list = []
        for item in self._cypher_map:
            file_dict = {}
            if self._cypher_map[item]["csv"]:
                file_dict["url"] = self._cypher_map[item]["csv"]
                file_dict["cql"] = self._cypher_map[item]["cypher"]
                file_dict["chunk_size"] = batch_size
                self._config_files_list.append(file_dict)

    def generate_pyingest_yaml_file(
        self, file_name: str = "pyingest_config", batch_size: int = 100
    ) -> None:
        """
        Generate the PyIngest yaml file.
        """

        if self.file_output_dir != "":
            os.makedirs(self.file_output_dir, exist_ok=True)

        with open(f"./{self.file_output_dir}{file_name}.yml", "w") as config_yaml:
            config_yaml.write(self.generate_pyingest_yaml_string(batch_size=batch_size))

    def generate_pyingest_yaml_string(self, batch_size: int = 100) -> str:
        """
        Generate the PyIngest yaml in string format.
        """

        self._generate_base_information(batch_size=batch_size)

        final_yaml = {}
        final_yaml["files"] = self._config_files_list
        config_dump = yaml.dump(final_yaml)

        to_return = (
            f"server_uri: {self.uri}\n"
            + f"admin_user: {self.username}\n"
            + f"admin_pass: {self.password}\n"
            + f"database: {self.database}\n"
            + "basepath: ./\n\n"
            + "pre_ingest:\n"
        )
        for constraint in self._constraints:
            to_return += f"  - {self._constraints[constraint]}"
        to_return += config_dump

        return to_return

    def generate_constraints_cypher_file(self, file_name: str = "constraints") -> None:
        """
        Generate the Constraints cypher file.
        """

        if self.file_output_dir != "":
            os.makedirs(self.file_output_dir, exist_ok=True)

        with open(
            f"./{self.file_output_dir}{file_name}.cypher", "w"
        ) as constraints_cypher:
            constraints_cypher.write(self.generate_constraints_cypher_string())

    def generate_constraints_cypher_string(self) -> str:
        """
        Generate the Constraints cypher file in string format.
        """

        if not self._constraints:
            self._generate_base_information()

        to_return = ""

        for constraint in self._constraints:
            to_return = to_return + self._constraints[constraint]

        return to_return

    def generate_load_csv_file(
        self, file_name: str = "load_csv", batch_size: int = 100, method: str = "api"
    ) -> None:
        """
        Generate the load_csv cypher file.
        """

        if self.file_output_dir != "":
            os.makedirs(self.file_output_dir, exist_ok=True)

        with open(f"./{self.file_output_dir}{file_name}.cypher", "w") as load_csv_file:
            load_csv_file.write(
                self.generate_load_csv_string(batch_size=batch_size, method=method)
            )

    def generate_load_csv_string(
        self, batch_size: int = 100, method: str = "api"
    ) -> str:
        """
        Generate the load_csv cypher in string format.
        """

        self._generate_base_information(batch_size=batch_size, method=method)

        to_return = ""

        for constraint in self._constraints:
            to_return = to_return + self._constraints[constraint]

        for item in self._cypher_map:
            to_return = to_return + self._cypher_map[item]["cypher_loadcsv"]

        return to_return


def generate_constraints_key(
    label_or_type: str, unique_property: Union[str, List[str]]
) -> str:
    """
    Generate the key for a unique or node key constraint.
    """
    if isinstance(unique_property, str):
        return f"{label_or_type.lower()}_{unique_property.lower()}"
    else:
        return (
            f"{label_or_type.lower()}_{'_'.join([x.lower() for x in unique_property])}"
        )


def generate_constraint(label_or_type: str, unique_property: str) -> str:
    """
    Generate a constrant string.
    """

    return f"CREATE CONSTRAINT {label_or_type.lower()}_{unique_property.lower()} IF NOT EXISTS FOR (n:{label_or_type}) REQUIRE n.{unique_property} IS UNIQUE;\n"


def generate_match_node_clause(node: Node) -> str:
    """
    Generate a MATCH node clause.
    """

    return (
        "MATCH (n:"
        + node.label
        + " {"
        + f"{generate_set_unique_property(node.node_key_mapping or node.unique_properties_column_mapping)}"
        + "})"
    )


def generate_match_same_node_labels_clause(node: Node) -> str:
    """
    Generate the two match statements for node with two unique csv mappings.
    This is used when a relationship connects two nodes with the same label.
    An example: (:Person{name: row.person_name})-[:KNOWS]->(:Person{name:row.knows_person})
    """

    from_unique, to_unique = [
        (
            "{" + f"{prop}: row.{csv_mapping[0]}" + "}",
            "{" + f"{prop}: row.{csv_mapping[1]}" + "}",
        )
        for prop, csv_mapping in node.unique_properties_column_mapping.items()
        if isinstance(csv_mapping, list)
    ][0]

    return f"""MATCH (source:{node.label} {from_unique})
MATCH (target:{node.label} {to_unique})"""


def generate_set_property(property_column_mapping: Dict[str, str]) -> str:
    """
    Generate a set property string.
    """

    temp_set_list = []

    for prop, col in property_column_mapping.items():
        temp_set_list.append(f"n.{prop} = row.{col}")

    result = ", ".join(temp_set_list)

    if not result == "":
        result = f"SET {result}"

    return result


def generate_set_unique_property(
    unique_properties_column_mapping: Dict[str, Union[str, List[str]]]
) -> str:
    """
    Generate the unique properties to match a node on within a MERGE statement.
    Returns: unique_property_match_component
    """

    res = [
        (
            f"{prop}: row.{csv_mapping[0]}"
            if isinstance(csv_mapping, list)
            else f"{prop}: row.{csv_mapping}"
        )
        for prop, csv_mapping in unique_properties_column_mapping.items()
    ]
    return ", ".join(res)


def generate_merge_node_clause_standard(node: Node) -> str:
    """
    Generate a MERGE node clause.
    """

    return f"""WITH $dict.rows AS rows
UNWIND rows AS row
MERGE (n:{node.label} {{{generate_set_unique_property(node.node_key_mapping or node.unique_properties_column_mapping)}}})
{generate_set_property(node.nonunique_properties_mapping_for_set_clause)}"""


def generate_merge_node_load_csv_clause(
    node: Node,
    csv_name: str,
    method: str = "api",
    batch_size: int = 10000,
) -> str:
    """
    Generate a MERGE node clause for the LOAD CSV method.
    """

    command = ":auto " if method == "browser" else ""
    return f"""{command}LOAD CSV WITH HEADERS FROM 'file:///{csv_name}' as row
CALL {{
    WITH row
    MERGE (n:{node.label} {{{generate_set_unique_property(node.node_key_mapping or node.unique_properties_column_mapping)}}})
    {generate_set_property(node.nonunique_properties_mapping_for_set_clause)}
}} IN TRANSACTIONS OF {str(batch_size)} ROWS;
"""


def generate_merge_relationship_clause_standard(
    relationship: Relationship, source_node: Node, target_node: Node
) -> str:
    """
    Generate a MERGE relationship clause.
    """
    if source_node.label == target_node.label:
        return f"""WITH $dict.rows AS rows
UNWIND rows as row
{generate_match_same_node_labels_clause(node=source_node)}
MERGE (source)-[n:{relationship.type}]->(target)
{generate_set_property(relationship.nonunique_properties_mapping_for_set_clause)}"""
    else:
        return f"""WITH $dict.rows AS rows
UNWIND rows as row
{generate_match_node_clause(source_node).replace('(n:', '(source:')}
{generate_match_node_clause(target_node).replace('(n:', '(target:')}
MERGE (source)-[n:{relationship.type}]->(target)
{generate_set_property(relationship.nonunique_properties_mapping_for_set_clause)}"""


def generate_merge_relationship_load_csv_clause(
    relationship: Relationship,
    source_node: Node,
    target_node: Node,
    csv_name: str,
    method: str = "api",
    batch_size: int = 10000,
) -> str:
    """
    Generate a MERGE relationship clause for the LOAD CSV method.
    """

    command = ":auto " if method == "browser" else ""
    if source_node.label == target_node.label:
        return f"""{command}LOAD CSV WITH HEADERS FROM 'file:///{csv_name}' as row
CALL {{
    WITH row
    {generate_match_same_node_labels_clause(node=source_node)}
    MERGE (source)-[n:{relationship.type}]->(target)
    {generate_set_property(relationship.nonunique_properties_mapping_for_set_clause)}
}} IN TRANSACTIONS OF {str(batch_size)} ROWS;
"""
    else:
        return f"""{command}LOAD CSV WITH HEADERS FROM 'file:///{csv_name}' as row
CALL {{
    WITH row
    {generate_match_node_clause(source_node).replace('(n:', '(source:')}
    {generate_match_node_clause(target_node).replace('(n:', '(target:')}
    MERGE (source)-[n:{relationship.type}]->(target)
    {generate_set_property(relationship.nonunique_properties_mapping_for_set_clause)}
}} IN TRANSACTIONS OF {str(batch_size)} ROWS;
"""


def generate_node_key_constraint(
    label: str, unique_property: Union[str, List[str]]
) -> str:
    """
    Generate a node key constraint.
    """
    props = "(" + ", ".join([f"n.{x}" for x in unique_property]) + ")"
    return f"""CREATE CONSTRAINT {generate_constraints_key(label_or_type=label, unique_property=unique_property)} IF NOT EXISTS FOR (n:{label}) REQUIRE {props} IS NODE KEY;\n"""


def generate_relationship_key_constraint(
    type: str, unique_property: Union[str, List[str]]
) -> str:
    """
    Generate a relationship key constraint.
    """
    props = "(" + ", ".join([f"r.{x}" for x in unique_property]) + ")"
    return f"""CREATE CONSTRAINT {generate_constraints_key(label_or_type=type, unique_property=unique_property)} IF NOT EXISTS FOR ()-[r:{type}]-() REQUIRE {props} IS RELATIONSHIP KEY;\n"""
