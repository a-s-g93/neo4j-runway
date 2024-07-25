"""
This file contains the code to generate ingestion code.
"""

import os
from typing import Dict, List, Any, Union
import warnings

import yaml

from .cypher import *
from ..models import DataModel


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


def lowercase_first_letter(s: str):
    return s[0].lower() + s[1:]


class IngestionGenerator:
    """
    Class responsible for generating the ingestion code.
    """

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
        """
        Class responsible for generating the ingestion code.

        Attributes
        ----------
        data_model : DataModel
            The data model to base ingestion code on.
        csv_name : str, optional
            The CSV containing the data. If data is contained in multiple CSVs,
            then this should be "" and CSVs noted in the data model, by default ""
        username : Union[str, None], optional
            The username used to connect to Neo4j, by default None
        password : Union[str, None], optional
            The password used to connect to Neo4j, by default None
        uri : Union[str, None], optional
            The uri of the Neo4j instance, by default None
        database : Union[str, None], optional
            The database within the Neo4j instance to load the data, by default None
        csv_dir : str, optional
            The location of the CSV file(s), by default ""
        file_output_dir : str, optional
            The location that generated files should be saved to, by default ""
        """

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

    warnings.warn(
        """The IngestionGenerator class will be removed in future releases! 
    Please instead use dedicated code generation classes: PyIngestConfigGenerator, LoadCSVCodeGenerator, StandardCypherCodeGenerator
    You can use these classes by importing like so: from neo4j_runway.code_generation import `desired class`"""
    )

    def _generate_base_information(
        self,
        method: str = "api",
        batch_size: int = 100,
        field_separator: str = None,
        pyingest_file_config: Dict[str, Any] = {},
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
            self._cypher_map[lowercase_first_letter(node.label)] = {
                "cypher": literal_unicode(
                    generate_merge_node_clause_standard(
                        node=node, strict_typing=strict_typing
                    )
                ),
                "cypher_loadcsv": literal_unicode(
                    generate_merge_node_load_csv_clause(
                        node=node,
                        csv_name=(
                            node.csv_name if self.csv_name == "" else self.csv_name
                        ),
                        method=method,
                        batch_size=batch_size,
                        strict_typing=strict_typing,
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
            self._cypher_map[f"{rel.source}_{rel.target}"] = {
                "cypher": literal_unicode(
                    generate_merge_relationship_clause_standard(
                        relationship=rel,
                        source_node=source,
                        target_node=target,
                        strict_typing=strict_typing,
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
                        strict_typing=strict_typing,
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

                # set globals
                file_dict["chunk_size"] = batch_size
                if field_separator:
                    file_dict["field_separator"] = field_separator

                # set distict file params
                if self._cypher_map[item]["csv"] in pyingest_file_config:
                    if (
                        "batch_size"
                        in pyingest_file_config[self._cypher_map[item]["csv"]]
                    ):
                        file_dict["chunk_size"] = pyingest_file_config[
                            self._cypher_map[item]["csv"]
                        ]["batch_size"]
                    if (
                        "field_separator"
                        in pyingest_file_config[self._cypher_map[item]["csv"]]
                    ):
                        file_dict["field_separator"] = pyingest_file_config[
                            self._cypher_map[item]["csv"]
                        ]["field_separator"]
                    if (
                        "skip_records"
                        in pyingest_file_config[self._cypher_map[item]["csv"]]
                    ):
                        file_dict["skip_records"] = pyingest_file_config[
                            self._cypher_map[item]["csv"]
                        ]["skip_records"]
                    if (
                        "skip_file"
                        in pyingest_file_config[self._cypher_map[item]["csv"]]
                    ):
                        file_dict["skip_file"] = pyingest_file_config[
                            self._cypher_map[item]["csv"]
                        ]["skip_file"]

                self._config_files_list.append(file_dict)

    def _format_pyingest_file_config_key(self, config_key: str) -> str:
        """
        Format the key to match with cypher_map keys.
        """

        if f"$BASE/{self.csv_dir}" not in config_key:
            config_key = f"$BASE/{self.csv_dir}{config_key}"
        if not config_key.endswith(".csv"):
            config_key = config_key + ".csv"

        return config_key

    def generate_pyingest_yaml_file(
        self,
        file_name: str = "pyingest_config",
        global_batch_size: int = 100,
        global_field_separator: str = None,
        pyingest_file_config: Dict[str, Any] = {},
        pre_ingest_code: Union[str, List[str], None] = None,
        post_ingest_code: Union[str, List[str], None] = None,
        strict_typing: bool = True,
    ) -> None:
        """
        Generate the PyIngest YAML config file.

        Parameters
        ----------
        file_name : str, optional
            Name of the file, by default "pyingest_config"
        global_batch_size : int, optional
            The desired batch size for all files, by default 100
        global_field_separator: str, optional
            The separator used for all CSV files, by default ","
        pyingest_file_config: Dict[str, Any], optional
            A dictionary containing individual file parameters.
            Supported parameters are: batch_size <int>, skip_records <int>, skip_file <int> and field_separator <str>
        pre_ingest_code : Union[str, List[str], None], optional
            Code to be run before data is ingested. This should include any constraints or indexes that will not be auto-generated by Runway.
        post_ingest_code : Union[str, List[str], None], optional
            Code to be run after all data is ingested.
            Can be either a String of cypher code, .cypher file filepath or list of cypher commands.
            Individual Cypher queries should be separated by a ';'.
        strict_typing : bool, optional
            Whether to use the types declared in the data model (True), or infer types during ingestion (False). By default True

        Returns
        ----------
        None
        """

        if self.file_output_dir != "":
            os.makedirs(self.file_output_dir, exist_ok=True)

        with open(f"./{self.file_output_dir}{file_name}.yml", "w") as config_yaml:
            config_yaml.write(
                self.generate_pyingest_yaml_string(
                    global_batch_size=global_batch_size,
                    global_field_separator=global_field_separator,
                    pyingest_file_config=pyingest_file_config,
                    pre_ingest_code=pre_ingest_code,
                    post_ingest_code=post_ingest_code,
                    strict_typing=strict_typing,
                )
            )

    def generate_pyingest_yaml_string(
        self,
        global_batch_size: int = 100,
        global_field_separator: str = None,
        pyingest_file_config: Dict[str, Any] = {},
        pre_ingest_code: Union[str, List[str], None] = None,
        post_ingest_code: Union[str, List[str], None] = None,
        strict_typing: bool = True,
    ) -> str:
        """
        Generate the PyIngest yaml in string format.

        Parameters
        ----------
        global_batch_size : int, optional
            The desired batch size for all files, by default 100
        global_field_separator: str, optional
            The separator used for all CSV files, by default ","
        pyingest_file_config: Dict[str, Any], optional
            A dictionary containing individual file parameters.
            Supported parameters are: batch_size <int>, skip_records <int>, skip_file <int> and field_separator <str>
        pre_ingest_code : Union[str, List[str], None], optional
            Code to be run before data is ingested. This should include any constraints or indexes that will not be auto-generated by Runway.
        post_ingest_code : Union[str, List[str], None], optional
            Code to be run after all data is ingested.
            Can be either a String of cypher code, .cypher file filepath or list of cypher commands.
            Individual Cypher queries should be separated by a ';'.
        strict_typing : bool, optional
            Whether to use the types declared in the data model (True), or infer types during ingestion (False). By defaut True

        Returns
        ----------
        str
            The yaml configuration in String format.
        """

        # reformat the keys if necessary
        if pyingest_file_config:
            pyingest_file_config = {
                self._format_pyingest_file_config_key(k): v
                for k, v in pyingest_file_config.items()
            }

        self._generate_base_information(
            batch_size=global_batch_size,
            field_separator=global_field_separator,
            pyingest_file_config=pyingest_file_config,
            strict_typing=strict_typing,
        )

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
        if pre_ingest_code:
            pre_ingest_code_string = format_pyingest_pre_or_post_ingest_code(
                data=pre_ingest_code
            )
            to_return += pre_ingest_code_string

        for constraint in self._constraints:
            to_return += f"  - {self._constraints[constraint]}"
        to_return += config_dump

        if post_ingest_code:
            post_ingest_code_string = format_pyingest_pre_or_post_ingest_code(
                data=post_ingest_code
            )
            to_return += "\npost_ingest:\n" + post_ingest_code_string

        return to_return

    def generate_constraints_cypher_file(self, file_name: str = "constraints") -> None:
        """
        Generate the Constraints cypher file.

        Parameters
        ----------
        file_name : str, optional
            Name of the file, by default "constraints"

        Returns
        ----------
        None
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

        Returns
        ----------
        str
            The constraints Cypher in String format.
        """

        if not self._constraints:
            self._generate_base_information()

        to_return = ""

        for constraint in self._constraints:
            to_return = to_return + self._constraints[constraint]

        return to_return

    def generate_load_csv_file(
        self,
        file_name: str = "load_csv",
        batch_size: int = 100,
        method: str = "api",
        strict_typing: bool = True,
    ) -> None:
        """
        Generate the LOAD CSV Cypher file.

        Parameters
        ----------
        file_name : str, optional
            Name of the file, by default "load_csv"
        batch_size : int, optional
            The desired batch size, by default 100
        method : str, optional
            The method that LOAD CSV will be run. Must be either "api" or "browser". By default "api"
        strict_typing: bool, optional
            Whether to use the types declared in the data model (True), or infer types during ingestion (False). By defaut True

        Returns
        ----------
        None
        """

        if self.file_output_dir != "":
            os.makedirs(self.file_output_dir, exist_ok=True)

        with open(f"./{self.file_output_dir}{file_name}.cypher", "w") as load_csv_file:
            load_csv_file.write(
                self.generate_load_csv_string(
                    batch_size=batch_size, method=method, strict_typing=strict_typing
                )
            )

    def generate_load_csv_string(
        self, batch_size: int = 100, method: str = "api", strict_typing: bool = True
    ) -> str:
        """
        Generate the load_csv cypher in string format.

        Parameters
        ----------
        batch_size : int, optional
            The desired batch size, by default 100
        method : str, optional
            The method that LOAD CSV will be run. Must be either "api" or "browser". By default "api"
        strict_typing: bool, optional
            Whether to use the types declared in the data model (True), or infer types during ingestion (False). By defaut True

        Returns
        ----------
        str
            The LOAD CSV Cypher in String format.
        """

        self._generate_base_information(
            batch_size=batch_size, method=method, strict_typing=strict_typing
        )

        to_return = ""

        for constraint in self._constraints:
            to_return = to_return + self._constraints[constraint]

        for item in self._cypher_map:
            to_return = to_return + self._cypher_map[item]["cypher_loadcsv"]

        return to_return
