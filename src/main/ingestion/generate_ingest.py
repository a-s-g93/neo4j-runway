import os

# import json
from typing import Dict, List, Any, Union

# import csv
import os

# import argparse
import yaml

# from yaml.representer import SafeRepresenter

from pydantic import BaseModel

from objects.data_model import DataModel

cypher_map = {}
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


class IngestionGenerator(BaseModel):

    data_model: DataModel
    username: Union[str, None] = None
    password: Union[str, None] = None
    uri: Union[str, None] = None
    database: Union[str, None] = None
    csv_name: str
    csv_dir: str = ""
    file_output_dir: str = ""

    config_files_list: Union[List[Dict[str, Any]], None] = []
    constraints: Dict[str, str] = {}
    cypher_map: Dict[str, Dict[str, Any]] = {}

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)

        self._generate_base_information()

    @staticmethod
    def _generate_constraints_key(node_label: str, unique_property: str) -> str:
        """
        Generate the key for a unique constraint.
        """

        return f"{node_label.lower()}_{unique_property.lower()}"

    @staticmethod
    def _generate_constraint(node_label: str, unique_property: str) -> str:
        """
        Generate a constrant string.
        """

        return f"CREATE CONSTRAINT {node_label.lower()}_{unique_property.lower()} IF NOT EXISTS FOR (n:{node_label}) REQUIRE n.{unique_property} IS UNIQUE;\n"

    @staticmethod
    def _generate_match_node_clause(
        node_label: str, unique_property_match_component: str
    ) -> str:
        """
        Generate a MATCH node clause.
        """

        return (
            "MATCH (n:" + node_label + "{" + f"{unique_property_match_component}" + "})"
        )

    @staticmethod
    def _generate_set_property(property_column_mapping: Dict[str, str]) -> str:
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

    @staticmethod
    def _generate_set_unique_property(unique_properties: List[str]) -> str:
        """
        Generate the unique properties to match a node on within a MERGE statement.
        Returns: unique_property_match_component
        """

        return ", ".join(unique_properties)

    @staticmethod
    def _generate_merge_node_clause_standard(
        node_label: str, unique_properties: str, non_unique_properties: str
    ) -> str:
        """
        Generate a MERGE node clause.
        """

        return (
            "WITH $dict.rows AS rows\nUNWIND rows AS row\nMERGE (n:"
            + node_label
            + " {"
            + unique_properties
            + "})\n"
            + non_unique_properties
        )

    @staticmethod
    def _generate_merge_node_load_csv_clause(
        node_label: str,
        unique_properties: str,
        non_unique_properties: str,
        batch_size: int = 10000,
    ) -> str:
        """
        Generate a MERGE node clause for the LOAD CSV method.
        """

        return (
            "LOAD CSV WITH HEADERS FROM 'file:///file_name' as row\nCALL {\n\tWITH row\n\tMERGE (n:"
            + node_label
            + " {"
            + unique_properties
            + "})\n"
            + non_unique_properties
            + "} IN TRANSACTIONS OF "
            + str(batch_size)
            + " ROWS;\n"
        )

    @staticmethod
    def _generate_merge_relationship_clause_standard(
        source_node: str,
        target_node: str,
        relationship_type: str,
        non_unique_properties_clause: str,
    ) -> str:
        """
        Generate a MERGE relationship clause.
        """
        # replace "(n:" so we don't catch alias names that end with "n"
        return f"""
            WITH $dict.rows AS rows\nUNWIND rows as row
            {source_node.replace('(n:', '(source:')}
            {target_node.replace('(n:', '(target:')}
            MERGE (source)-[:{relationship_type}]->(target)
            {non_unique_properties_clause}
            """

    @staticmethod
    def _generate_merge_relationship_load_csv_clause(
        source_node: str,
        target_node: str,
        relationship_type: str,
        non_unique_properties_clause: str,
        batch_size: int = 10000,
    ) -> str:
        """
        Generate a MERGE relationship clause for the LOAD CSV method.
        """

        return f"""
            LOAD CSV WITH HEADERS FROM 'file:///file_name' as row
            CALL {{
              WITH row
              {source_node.replace('(n:', '(source:')}
              {target_node.replace('(n:', '(target:')}
              MERGE (source)-[:{relationship_type}]->(target)
              {non_unique_properties_clause}
              }} IN TRANSACTIONS OF {batch_size} ROWS;
              """

    def _generate_base_information(self):
        for node in self.data_model.nodes:
            label = node.label
            props = node.property_column_mapping
            unique_constraints_parts = node.unique_constraints_column_mapping
            for k in unique_constraints_parts.keys():
                del props[k]
            csv_file = self.csv_name
            unique_constraints = []

            if len(unique_constraints_parts) > 0:
                for (
                    unique_property,
                    unique_property_csv_mapping,
                ) in unique_constraints_parts.items():
                    unique_constraints.append(
                        f"{unique_property}: row.{unique_property_csv_mapping}"
                    )
                    self.constraints[
                        self._generate_constraints_key(
                            node_label=label, unique_property=unique_property
                        )
                    ] = self._generate_constraint(
                        node_label=label, unique_property=unique_property
                    )

            print("constraints: ", self.constraints)
            set_property_string = self._generate_set_property(
                property_column_mapping=props
            )

            unique_property_match_component = self._generate_set_unique_property(
                unique_properties=unique_constraints
            )
            merge_str = self._generate_merge_node_clause_standard(
                node_label=label,
                unique_properties=unique_property_match_component,
                non_unique_properties=set_property_string,
            )
            load_csv_merge_str = self._generate_merge_node_load_csv_clause(
                node_label=label,
                unique_properties=unique_property_match_component,
                non_unique_properties=set_property_string,
                batch_size=10000,
            )
            nodes_map[lowercase_first_letter(label)] = self._generate_match_node_clause(
                node_label=label,
                unique_property_match_component=unique_property_match_component,
            )

            # add to cypher map
            self.cypher_map[lowercase_first_letter(label)] = {
                "cypher": literal_unicode(merge_str),
                "cypher_loadcsv": literal_unicode(load_csv_merge_str),
                "csv": f"$BASE/{self.csv_dir}{csv_file}",
            }
        print("cypher map: \n", self.cypher_map)
        model_map = {}
        ## get relationships
        for rel in self.data_model.relationships:
            rel_type = rel.type
            src_node_label = rel.source
            target_node_label = rel.target
            props = node.property_column_mapping
            unique_constraints_parts = node.unique_constraints_column_mapping

            for k in unique_constraints_parts.keys():
                del props[k]
            csv_file = self.csv_name
            unique_constraints = []

            if len(unique_constraints_parts) > 0:
                for (
                    unique_property,
                    unique_property_csv_mapping,
                ) in unique_constraints_parts.items():
                    unique_constraints.append(
                        f"{unique_property}: row.{unique_property_csv_mapping}"
                    )
                    self.constraints[
                        self._generate_constraints_key(
                            node_label=label, unique_property=unique_property
                        )
                    ] = self._generate_constraint(
                        node_label=label, unique_property=unique_property
                    )

            print("constraints: ", self.constraints)
            set_property_string = self._generate_set_property(
                property_column_mapping=props
            )

            unique_property_match_component = self._generate_set_unique_property(
                unique_properties=unique_constraints
            )
            model_map[
                f"{lowercase_first_letter(src_node_label)}_{lowercase_first_letter(target_node_label)}"
            ] = {
                "source": {
                    "node": f"{nodes_map[lowercase_first_letter(src_node_label)]}"
                },
                "target": {
                    "node": f"{nodes_map[lowercase_first_letter(target_node_label)]}"
                },
                "csv": f"{self.csv_name}",
                "relationship": {"rel": rel_type},
            }
            model_maps.append(model_map)
            print("model maps: ", model_maps)
            for mapitem in model_map:
                if model_map[mapitem]["csv"] is not None:
                    merge_str = self._generate_merge_relationship_clause_standard(
                        source_node=model_map[mapitem]["source"]["node"],
                        target_node=model_map[mapitem]["target"]["node"],
                        relationship_type=model_map[mapitem]["relationship"]["rel"],
                    )

                    load_csv_merge_str = (
                        self._generate_merge_relationship_load_csv_clause(
                            source_node=model_map[mapitem]["source"]["node"],
                            target_node=model_map[mapitem]["target"]["node"],
                            relationship_type=model_map[mapitem]["relationship"]["rel"],
                            batch_size=10000,
                        )
                    )

                    self.cypher_map[mapitem] = {
                        "cypher": literal_unicode(merge_str),
                        "cypher_loadcsv": literal_unicode(load_csv_merge_str),
                        "csv": f"$BASE/{self.csv_dir}{model_map[mapitem]['csv']}",
                    }

        self.config_files_list = []
        for item in self.cypher_map:
            file_dict = {}
            if self.cypher_map[item]["csv"]:
                file_dict["url"] = self.cypher_map[item]["csv"]
                file_dict["cql"] = self.cypher_map[item]["cypher"]
                file_dict["chunk_size"] = 100
                self.config_files_list.append(file_dict)

        self.config_files_list = []
        for item in self.cypher_map:
            file_dict = {}
            if self.cypher_map[item]["csv"]:
                file_dict["url"] = self.cypher_map[item]["csv"]
                file_dict["cql"] = self.cypher_map[item]["cypher"]
                file_dict["chunk_size"] = 100
                self.config_files_list.append(file_dict)

    def generate_pyingest_yaml_file(self, file_name: str = "pyingest_config") -> None:
        """
        Generate the PyIngest yaml file.
        """

        if self.file_output_dir != "":
            os.makedirs(self.file_output_dir, exist_ok=True)

        with open(f"./{self.file_output_dir}{file_name}.yml", "w") as config_yaml:
            config_yaml.write(self.generate_pyingest_yaml_string())

    def generate_pyingest_yaml_string(self) -> str:
        """
        Generate the PyIngest yaml in string format.
        """

        final_yaml = {}
        final_yaml["files"] = self.config_files_list
        config_dump = yaml.dump(final_yaml)

        to_return = (
            f"server_uri: {self.uri}\n"
            + f"admin_user: {self.username}\n"
            + f"admin_pass: {self.password}\n"
            + f"database: {self.database}\n"
            + "basepath: file:./\n\n"
            + "pre_ingest:\n"
        )
        for constraint in self.constraints:
            to_return += f"  - {self.constraints[constraint]}"
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
        to_return = ""

        for constraint in self.constraints:
            to_return = to_return + self.constraints[constraint]

        return to_return

    def generate_load_csv_file(self, file_name: str = "load_csv") -> None:
        """
        Generate the load_csv cypher file.
        """

        if self.file_output_dir != "":
            os.makedirs(self.file_output_dir, exist_ok=True)

        with open(f"./{self.file_output_dir}{file_name}.cypher", "w") as load_csv_file:
            load_csv_file.write(self.generate_load_csv_string())

    def generate_load_csv_string(self) -> str:
        """
        Generate the load_csv cypher in string format.
        """
        to_return = ""

        for constraint in self.constraints:
            to_return = to_return + self.constraints[constraint]

        for item in self.cypher_map:
            to_return = to_return + self.cypher_map[item]["cypher_loadcsv"]

        return to_return
