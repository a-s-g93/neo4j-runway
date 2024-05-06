"""
This is a modified PyIngest file for Neo4j Runway. It currently only supports Pandas DataFrame ingestion.
"""

import datetime

from neo4j import GraphDatabase
import numpy as np
import pandas as pd
import yaml


config = dict()


class LocalServer(object):

    def __init__(self):
        self._driver = GraphDatabase.driver(
            config["server_uri"], auth=(config["admin_user"], config["admin_pass"])
        )
        self.db_config = {}
        self.database = config["database"] if "database" in config else None
        if self.database is not None:
            self.db_config["database"] = self.database
        self.basepath = config["basepath"] if "basepath" in config else None

    def close(self):
        self._driver.close()

    def get_params(self, file):
        params = dict()
        params["skip_records"] = file.get("skip_records") or 0
        params["compression"] = file.get("compression") or "none"
        # if params["compression"] not in supported_compression_formats:
        #     print("Unsupported compression format: {}", params["compression"])

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
        Load a Pandas DataFrame directly using a PyIngest yaml config file.
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

    def pre_ingest(self):
        if "pre_ingest" in config:
            statements = config["pre_ingest"]
            if len(statements) > 0:
                with self._driver.session(**self.db_config) as session:
                    for statement in statements:
                        session.run(statement)
            else:
                print("no pre ingest scripts found.")

    def post_ingest(self):
        if "post_ingest" in config:
            statements = config["post_ingest"]
            if len(statements) > 0:
                with self._driver.session(**self.db_config) as session:
                    for statement in statements:
                        session.run(statement)
            else:
                print("no post ingest scripts found.")


def load_config(configuration):
    global config
    config = yaml.safe_load(configuration)


def PyIngest(yaml_string: str, dataframe: pd.DataFrame) -> None:
    # configuration = sys.argv[1]
    load_config(yaml_string)
    server = LocalServer()
    server.pre_ingest()
    file_list = config["files"]
    for file in file_list:
        server.load_dataframe(file, dataframe=dataframe)
    server.post_ingest()
    server.close()
