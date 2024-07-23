"""
This is a modified PyIngest file for Neo4j Runway. It currently only supports Pandas DataFrame and CSV ingestion.
"""

import datetime
from typing import Optional, Union
import warnings

from neo4j import GraphDatabase
import numpy as np
import pandas as pd
import yaml


global_config = dict()


class LocalServer(object):
    """
    Handles data ingestion.
    """

    def __init__(self):
        self._driver = GraphDatabase.driver(
            global_config["server_uri"],
            auth=(global_config["admin_user"], global_config["admin_pass"]),
        )
        self.db_config = {}
        self.database = (
            global_config["database"] if "database" in global_config else None
        )
        if self.database is not None:
            self.db_config["database"] = self.database
        self.basepath = (
            global_config["basepath"] if "basepath" in global_config else None
        )

    def close(self):
        self._driver.close()

    def get_params(self, file):
        params = dict()
        params["skip_records"] = file.get("skip_records") or 0
        params["compression"] = file.get("compression") or "none"

        file_url = file["url"]
        if self.basepath and file_url.startswith("$BASE"):
            file_url = file_url.replace("$BASE", self.basepath, 1)
        params["url"] = file_url
        print("File {}", params["url"])
        params["cql"] = file["cql"]
        params["chunk_size"] = file.get("chunk_size") or 1000
        params["field_sep"] = file.get("field_separator") or ","
        return params

    def load_dataframe(self, file, dataframe: pd.DataFrame) -> None:
        """
        Load a Pandas DataFrame directly using a PyIngest yaml global_config file.
        """
        with self._driver.session(**self.db_config) as session:
            params = self.get_params(file)

            partition = max(1, int(len(dataframe) / params["chunk_size"]))

            for i, rows in enumerate(np.array_split(dataframe, partition)):
                print("loading...", i, datetime.datetime.now(), flush=True)
                # Chunk up the rows to enable additional fastness :-)
                rows_dict = {"rows": rows.fillna(value="").to_dict("records")}
                session.run(params["cql"], dict=rows_dict).consume()

        print("{} : Completed file", datetime.datetime.now())

    def load_csv(self, file):
        with self._driver.session(**self.db_config) as session:
            params = self.get_params(file)

            # check if we load this file...
            skip = params["skip_file"] if "skip_file" in params else False
            if skip:
                return
            with open(params["url"]) as openfile:
                # Grab the header from the file and pass that to pandas.  This allow the header
                # to be applied even if we are skipping lines of the file
                header = str(openfile.readline()).strip().split(params["field_sep"])

                # Pandas' read_csv method is highly optimized and fast :-)
                row_chunks = pd.read_csv(
                    openfile,
                    dtype=str,
                    sep=params["field_sep"],
                    on_bad_lines="skip",
                    index_col=False,
                    skiprows=params["skip_records"],
                    names=header,
                    low_memory=False,
                    engine="c",
                    compression="infer",
                    header=None,
                    chunksize=params["chunk_size"],
                )

                for i, rows in enumerate(row_chunks):
                    print(params["url"], i, datetime.datetime.now(), flush=True)
                    # Chunk up the rows to enable additional fastness :-)
                    rows_dict = {"rows": rows.fillna(value="").to_dict("records")}
                    session.run(params["cql"], dict=rows_dict).consume()

        print("{} : Completed file", datetime.datetime.now())

    def pre_ingest(self):
        if "pre_ingest" in global_config:
            statements = global_config["pre_ingest"]
            if len(statements) > 0:
                with self._driver.session(**self.db_config) as session:
                    for statement in statements:
                        session.run(statement)
            else:
                print("no pre ingest scripts found.")

    def post_ingest(self):
        if "post_ingest" in global_config:
            statements = global_config["post_ingest"]
            if len(statements) > 0:
                with self._driver.session(**self.db_config) as session:
                    for statement in statements:
                        session.run(statement)
            else:
                print("no post ingest scripts found.")


def load_config(configuration):
    global global_config
    global_config = yaml.safe_load(configuration)


def PyIngest(
    config: str = None, dataframe: Optional[pd.DataFrame] = None, **kwargs
) -> None:
    """
    Function to ingest data according to a configuration YAML.
    This is a modified version of the original PyIngest that focuses on loading local files.

    Parameters
    ----------
    config : str
        A string representation of the YAML file that is generated by the IngestionGenerator class.
        May also be a filepath to a YAML file.
    dataframe : Optional[pd.DataFrame], optional
        The data to ingest in Pandas DataFrame format.
        If None, then will search for CSVs according to the urls in YAML config, by default None
    yaml_string : str
        A string representation of the YAML file that is generated by the IngestionGenerator class.
        May also be a filepath to a YAML file.
        .. deprecated:: 0.5.2
            Replaced by the `config` arg as this is more encompassing.


    """
    if "yaml_string" in kwargs:
        load_config(get_yaml(kwargs["yaml_string"]))
        warnings.warn(
            "the yaml_string parameter will be depreciated in future releases. Please use the 'config' to identify the YAML file instead."
        )
    else:
        load_config(get_yaml(config))

    server = LocalServer()
    server.pre_ingest()
    file_list = global_config["files"]
    for file in file_list:
        if dataframe is not None:
            server.load_dataframe(file, dataframe=dataframe)
        else:
            server.load_csv(file)
    server.post_ingest()
    server.close()


def get_yaml(data: str) -> str:
    # yaml already in String format
    if (
        isinstance(data, str)
        and ".yml" not in data.lower()
        and ".yaml" not in data.lower()
    ):
        return data
    # load the yaml
    elif isinstance(data, str) and (".yml" in data.lower() or ".yaml" in data.lower()):
        with open(data, "r") as f:
            yml_file = f.read()

        return yml_file
    else:
        raise ValueError(
            "Unable to parse the provided yaml_string argument. Please pass a yaml file in String format or a file path to the desired yaml file."
        )
