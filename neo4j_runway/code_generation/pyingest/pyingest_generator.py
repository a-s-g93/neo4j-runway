"""
This file contains the code to generate PyIngest configuration code.
"""

import os
from typing import Any, Dict, List, Optional, Union

import yaml


from ..base import BaseCodeGenerator
from ..cypher import format_pyingest_pre_or_post_ingest_code
from ...models.core import DataModel
from .._utils.prep_yaml import prep_yaml

class PyIngestConfigGenerator(BaseCodeGenerator):
    """
    Class responsible for generating the ingestion code.
    """

    def __init__(
        self,
        data_model: DataModel,
        file_directory: str = "./",
        file_output_directory: str = "./",
        csv_name: str = "",
        strict_typing: bool = True,
        username: Optional[str] = None,
        password: Optional[str] = None,
        uri: Optional[str] = None,
        database: Optional[str] = None,
        global_batch_size: int = 100,
        global_field_separator: Optional[str] = None,
        pyingest_file_config: Optional[Dict[str, Any]] = dict(),
        pre_ingest_code: Optional[Union[str, List[str]]] = None,
        post_ingest_code: Optional[Union[str, List[str]]] = None,
    ):
        """
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
        username : Union[str, None], optional
            The Neo4j username. Providing credentials here will write them into the configuration. Use with caution! By default None
        password : Union[str, None], optional
            The Neo4j password. Providing credentials here will write them into the configuration. Use with caution! By default None
        uri : Union[str, None], optional
            The Neo4j uri. Providing credentials here will write them into the configuration. Use with caution! By default None
        database : Union[str, None], optional
            The Neo4j database. Providing credentials here will write them into the configuration. Use with caution! By default None
        global_batch_size : int, optional
            The global batch size to use. Will be overwritten by any batch sizes declared in the pyingest_file_config arg. By default 100
        global_field_separator : Optional[str], optional
            The global field separator to use. Will be overwritten by any batch sizes declared in the pyingest_file_config arg. By default None
        pyingest_file_config : Optional[Dict[str, Any]], optional
            Additional configuration parameters to inject into the final YAML configuration. Parameters are file specific.
            Supported parameters are: batch_size <int>, skip_records <int>, skip_file <int> and field_separator <str>. By default dict()
            Example: pyingest_config = {
                "A.csv": {"field_separator": "|", "skip_file": False, "skip_records": 5},
                "B.csv": {"skip_file": True, "batch_size": 1234},
            }
        pre_ingest_code : Union[str, List[str], None], optional
            Code to be run before data is ingested. This should include any constraints or indexes that will not be auto-generated by Runway. By default = None
        post_ingest_code : Union[str, List[str], None], optional
            Code to be run after all data is ingested. By default = None

        """
        super().__init__(
            data_model=data_model,
            file_directory=file_directory,
            file_output_directory=file_output_directory,
            csv_name=csv_name,
            strict_typing=strict_typing,
        )
        self.username: Union[str, None] = username
        self.password: Union[str, None] = password
        self.uri: Union[str, None] = uri
        self.database: Union[str, None] = database
        self.global_batch_size = global_batch_size
        self.global_field_separator = global_field_separator
        self.pyingest_file_config = pyingest_file_config
        self.pre_ingest_code = pre_ingest_code
        self.post_ingest_code = post_ingest_code
        
        self._config_files_list = list()

        # reformat the keys if necessary
        if self.pyingest_file_config:
            self.pyingest_file_config = {
                self._format_pyingest_file_config_key(k): v
                for k, v in self.pyingest_file_config.items()
            }

        # add config params to files
        for item in self._cypher:
            file_dict = dict()
            if self._cypher[item]["csv"]:
                file_dict["url"] = self._cypher[item]["csv"]
                file_dict["cql"] = self._cypher[item]["cypher"]

                # set globals
                file_dict["chunk_size"] = self.global_batch_size
                if self.global_field_separator:
                    file_dict["field_separator"] = self.global_field_separator

                # set distict file params
                if self._cypher[item]["csv"] in self.pyingest_file_config:
                    if "batch_size" in self.pyingest_file_config[self._cypher[item]["csv"]]:
                        file_dict["chunk_size"] = self.pyingest_file_config[
                            self._cypher[item]["csv"]
                        ]["batch_size"]
                    if (
                        "field_separator"
                        in self.pyingest_file_config[self._cypher[item]["csv"]]
                    ):
                        file_dict["field_separator"] = self.pyingest_file_config[
                            self._cypher[item]["csv"]
                        ]["field_separator"]
                    if (
                        "skip_records"
                        in self.pyingest_file_config[self._cypher[item]["csv"]]
                    ):
                        file_dict["skip_records"] = self.pyingest_file_config[
                            self._cypher[item]["csv"]
                        ]["skip_records"]
                    if "skip_file" in self.pyingest_file_config[self._cypher[item]["csv"]]:
                        file_dict["skip_file"] = self.pyingest_file_config[
                            self._cypher[item]["csv"]
                        ]["skip_file"]

                self._config_files_list.append(file_dict)

    def _format_pyingest_file_config_key(self, config_key: str) -> str:
        """
        Format the key to match with cypher_map keys.
        """

        if f"$BASE/{self.file_dir}" not in config_key:
            config_key = f"$BASE/{self.file_dir}{config_key}"

        return config_key

    def generate_config_yaml(
        self,
        file_name: str = "pyingest_config.yaml",
    ) -> None:
        """
        Generate the PyIngest YAML config file.

        Parameters
        ----------
        file_name : str, optional
            Name of the file, by default "pyingest_config"

        Returns
        ----------
        None
        """

        if self.file_output_dir != "":
            os.makedirs(self.file_output_dir, exist_ok=True)

        with open(f"./{self.file_output_dir}{file_name}", "w") as config_yaml:
            config_yaml.write(self.generate_config_string())

    def generate_config_string(
        self,
    ) -> str:
        """
        Generate the PyIngest yaml in string format.

        Returns
        ----------
        str
            The yaml configuration in String format.
        """

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
        if self.pre_ingest_code:
            pre_ingest_code_string = format_pyingest_pre_or_post_ingest_code(
                data=self.pre_ingest_code
            )
            to_return += pre_ingest_code_string

        for constraint in self._constraints:
            to_return += f"  - {self._constraints[constraint]}"
        to_return += config_dump

        if self.post_ingest_code:
            post_ingest_code_string = format_pyingest_pre_or_post_ingest_code(
                data=self.post_ingest_code
            )
            to_return += "\npost_ingest:\n" + post_ingest_code_string

        return to_return
