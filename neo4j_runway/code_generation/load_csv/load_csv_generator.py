"""
This file contains the code to generate LOAD CSV code.
"""

import os
from typing import Dict, List, Any, Union

from ..base import BaseCodeGenerator
from ..cypher import (
    generate_merge_node_load_csv_clause,
    generate_merge_relationship_load_csv_clause,
)
from ...models import DataModel


class LoadCSVCodeGenerator(BaseCodeGenerator):
    """
    Class responsible for generating the LOAD CSV code.
    """

    def __init__(
        self,
        data_model: DataModel,
        file_directory: str = "./",
        file_output_directory: str = "./",
        csv_name: str = "",
        strict_typing: bool = True,
        batch_size: int = 100,
        method: str = "api",
    ):
        """
        Class responsible for generating the LOAD CSV code.

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
        batch_size : int, optional
            The desired batch size, by default 100
        method : str, optional
            The method that LOAD CSV will be run. Must be either "api" or "browser". By default "api"
        """

        super().__init__(
            data_model=data_model,
            file_directory=file_directory,
            file_output_directory=file_output_directory,
            csv_name=csv_name,
            strict_typing=strict_typing,
        )
        self.batch_size: int = batch_size
        self.method: str = method

    def generate_cypher_file(self, file_name: str = "load_csv.cypher") -> None:
        """
        Generate the LOAD CSV Cypher file.

        Parameters
        ----------
        file_name : str, optional
            The file name.

        Returns
        ----------
        None
        """

        if self.file_output_dir != "":
            os.makedirs(self.file_output_dir, exist_ok=True)

        with open(f"./{self.file_output_dir}{file_name}", "w") as load_csv_file:
            load_csv_file.write(self.generate_cypher_string())

    def generate_cypher_string(self) -> str:
        """
        Generate the load_csv cypher in string format.

        Returns
        ----------
        str
            The LOAD CSV Cypher in String format.
        """

        to_return = ""

        for constraint in self._constraints:
            to_return = to_return + self._constraints[constraint]

        for item in self._cypher:
            if "_" not in item:
                cypher = generate_merge_node_load_csv_clause(
                    csv_name=self._cypher[item]["csv"][6:],  # remove the $BASE/ prefix
                    method=self.method,
                    batch_size=self.batch_size,
                    standard_clause=self._cypher[item]["cypher"],
                )
            else:
                cypher = generate_merge_relationship_load_csv_clause(
                    csv_name=self._cypher[item]["csv"][6:],  # remove the $BASE/ prefix
                    method=self.method,
                    batch_size=self.batch_size,
                    standard_clause=self._cypher[item]["cypher"],
                )
            to_return = to_return + cypher

        return to_return
