import logging
import os
from typing import Any, Callable, Dict, List, Literal, Optional, Union

import pandas as pd
from IPython.display import (
    Markdown,
    display,
)

from ..database.neo4j import Neo4jGraph
from . import queries
from .cache import EDACache, create_eda_cache
from .report.template import create_eda_report

# supress some neo4j logging
logging.getLogger("neo4j").setLevel(logging.CRITICAL)


class GraphEDA:
    """
        The GraphEDA module contains queries that return
    information about the Neo4j database and its contents.

    The purpose of GraphEDA is to understand the characteristics
    of the data in graph form (nodes, relationships, and properties).
    This also helps identify errors and outliers in the data.

    The methods in this class primarily use Cypher to query and analyze
    data in the graph. The queries use Cypher because apoc.meta.schema
    uses sampling techniques and so the results are not necessarily deterministic.

    WARNING: The methods in this module can be computationally expensive.
    It is not recommended to use this module on massive Neo4j databases
    (i.e., nodes and relationships in the hundreds of millions)

    Attributes
    ----------

    database_version : str
        The database version
    database_edition : str
        The database edition
    report : str
        A report containing the results of EDA queries ran against the database
    """

    def __init__(self, graph: Optional[Neo4jGraph] = None):
        """
        Initialize a GraphEDA class.

        Parameters
        ----------
        graph : Optional[Neo4jGraph], optional
            The `Neo4jGraph` object to be used to run queries.
            If not provided, will attempt to create via environment variables., by default None

        Raises
        ------
        ValueError
            If unable to construct `Neo4jGraph` object from environment variables.
        """
        # instantiate Neo4jGraph
        if graph is None:
            try:
                self.graph = Neo4jGraph(
                    username=os.environ.get("NEO4J_USERNAME", "neo4j"),
                    password=os.environ.get("NEO4J_PASSWORD", "password"),
                    uri=os.environ.get("NEO4J_URI", "bolt://localhost:7687"),
                    database=os.environ.get("NEO4J_DATABASE", "neo4j"),
                )
            except Exception as e:
                raise ValueError(
                    f"Unable to initialize `Neo4jGraph` from environment variables. Must provide valid values for NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_URI and optionally NEO4J_DATABASE. Error: {e}"
                )
        elif isinstance(graph, Neo4jGraph):
            self.graph = graph
        else:
            raise ValueError(
                "Must provide a `Neo4jGraph` object or leave blank to initialize with environment variables."
            )

        self.cache: EDACache = create_eda_cache()
        self.report = "no report generated"

    @property
    def database_version(self) -> str:
        """The database version"""
        return self.graph.database_version

    @property
    def database_edition(self) -> str:
        """The database edition"""
        return self.graph.database_edition

    def run(self, refresh: bool = False) -> EDACache:
        """
        Run all analytics on the database. Results will be added to the cache.
        WARNING: The methods in this module can be computationally expensive.
        It is not recommended to use this module on massive Neo4j databases
        (i.e., nodes and relationships in the hundreds of millions)

        Parameters
        ----------
        refresh : bool, optional
            Whether to refresh all analytics regardless of if they've been previously ran, by default False

        Returns
        -------
        EDACache
            The results cache
        """

        for k in self.cache.keys():
            if refresh or self.cache.get(k) is None:
                method = getattr(self, k)
                method(refresh=refresh)

        return self.cache

    def create_eda_report(
        self,
        include_unlabeled_node_ids: bool = False,
        include_disconnected_node_ids: bool = False,
        include_node_degrees: bool = True,
        order_node_degrees_by: Literal["in", "out"] = "out",
        top_k_node_degrees: int = 5,
        save_file: bool = False,
        file_name: str = "eda_report.md",
        view_report: bool = True,
        notebook: bool = True,
    ) -> str:
        """
        Generate a report containing information from the `Neo4jGraph` and internal cache containing eda query results.
        The report may be output in Markdown format.

        Parameters
        ----------
        include_unlabeled_node_ids : bool, optional
            Whether to include the ids of unlabeled nodes, by default False
        include_disconnected_node_ids : bool, optional
            Whether to include the ids of disconnected nodes, by default False
        include_node_degrees : bool, optional
            Whether to include information on node degrees, by default True
        order_node_degrees_by : Literal["in", "out"], optional
            How to order the node degrees table, by default "out"
        top_k_node_degrees : int, optional
            How many rows to include in the node degrees table, by default 5
        save_file : bool, optional
            Whether to save the file, by default False
        file_name : str, optional
            The file name, if saving the file, by default eda_report.md
        view_report : bool, optional
            Whether to print the report upon completion, by default True
        notebook : bool, optional
            Whether the report will be displayed in a Python notebook, by default True

        Returns
        -------
        str
            The report in string format.
        """

        report = create_eda_report(
            graph=self.graph,
            eda_cache=self.cache,
            include_unlabeled_node_ids=include_unlabeled_node_ids,
            include_disconnected_node_ids=include_disconnected_node_ids,
            include_node_degrees=include_node_degrees,
            order_node_degrees_by=order_node_degrees_by,
            top_k_node_degrees=top_k_node_degrees,
            save_file=save_file,
            file_name=file_name,
        )

        self.report = report

        if save_file:
            self.save_report(file_name=file_name)

        if view_report:
            self.view_report(notebook=notebook)

        return self.report

    def save_report(self, file_name: str = "eda_report.md") -> None:
        """
        Save the report to a Markdown file.

        Parameters
        ----------
        file_name : str, optional
            The file name, by default "eda_report.md"
        """

        with open(file_name, "w") as f:
            f.write(self.report)

    def view_report(self, notebook: bool = True) -> None:
        """
        View the report.

        Parameters
        ----------
        notebook : bool, optional
            If viewing in a notebook setting, by default True
        """

        print(self.report) if not notebook else display(Markdown(self.report))

    def delete_cache(self) -> None:
        """
        Delete the query result cache.
        """

        self.cache = create_eda_cache()

    def _process_request(
        self,
        key_name: Literal[
            "database_indexes",
            "database_constraints",
            "node_count",
            "node_label_counts",
            "node_multi_label_counts",
            "node_properties",
            "relationship_count",
            "relationship_type_counts",
            "relationship_properties",
            "unlabeled_node_count",
            "unlabeled_node_ids",
            "disconnected_node_count",
            "disconnected_node_count_by_label",
            "disconnected_node_ids",
            "node_degrees",
        ],
        query_function: Callable[[Any, Any], Any],
        refresh: bool,
        as_dataframe: bool,
    ) -> Union[List[Dict[str, Any]], pd.DataFrame, int]:
        if refresh or self.cache.get(key_name) is None:
            self.cache[key_name] = query_function(  # type: ignore
                driver=self.graph.driver, database=self.graph.database
            )

        if as_dataframe:
            return pd.DataFrame(self.cache.get(key_name))

        return self.cache.get(key_name)

    def database_indexes(
        self, refresh: bool = False, as_dataframe: bool = True
    ) -> Union[List[Dict[str, Any]], pd.DataFrame]:
        """
        Method to identify the Neo4j database's indexes.

        Parameters
        ----------
        refresh : bool, optional
            Whether to re-query the databae, by default False
        as_dataframe : bool, optional
            Whether to return results as a Pandas DataFrame, by default True

        Returns
        -------
        Union[List[Dict[str, Any]], pd.DataFrame]
            The results as either a list of dictionaries or a Pandas DataFrame
        """

        return self._process_request(
            key_name="database_indexes",
            query_function=queries.get_database_indexes,
            refresh=refresh,
            as_dataframe=as_dataframe,
        )

    def database_constraints(
        self, refresh: bool = False, as_dataframe: bool = True
    ) -> Union[List[Dict[str, Any]], pd.DataFrame]:
        """
        Get the constraints for the graph database.

        Parameters
        ----------
        refresh : bool, optional
            Whether to re-query the databae, by default False
        as_dataframe : bool, optional
            Whether to return results as a Pandas DataFrame, by default True

        Returns
        -------
        Union[List[Dict[str, Any]], pd.DataFrame]
            The results as either a list of dictionaries or a Pandas DataFrame
        """

        return self._process_request(
            key_name="database_constraints",
            query_function=queries.get_database_constraints,
            refresh=refresh,
            as_dataframe=as_dataframe,
        )

    # graph node count
    def node_count(self, refresh: bool = False) -> int:
        """
        Count the total number of nodes in the graph.

        Parameters
        ----------
        refresh : bool, optional
            Whether to re-query the databae, by default False

        Returns
        -------
        int
            The number of nodes
        """

        response = self._process_request(
            key_name="node_count",
            query_function=queries.get_node_count,
            refresh=refresh,
            as_dataframe=False,
        )

        assert isinstance(response, int), "invalid response."

        return response

    def node_label_counts(
        self, refresh: bool = False, as_dataframe: bool = True
    ) -> Union[List[Dict[str, Any]], pd.DataFrame]:
        """
        Count the number of nodes associated with each
        unique label in the graph.

        Parameters
        ----------
        refresh : bool, optional
            Whether to re-query the databae, by default False
        as_dataframe : bool, optional
            Whether to return results as a Pandas DataFrame, by default True

        Returns
        -------
        Union[List[Dict[str, Any]], pd.DataFrame]
            The results as either a list of dictionaries or a Pandas DataFrame
        """

        return self._process_request(
            key_name="node_label_counts",
            query_function=queries.get_node_label_counts,
            refresh=refresh,
            as_dataframe=as_dataframe,
        )

    def node_multi_label_counts(
        self, refresh: bool = False, as_dataframe: bool = True
    ) -> Union[List[Dict[str, Any]], pd.DataFrame]:
        """
        Identify nodes in the graph that have multiple labels.

        Parameters
        ----------
        refresh : bool, optional
            Whether to re-query the databae, by default False
        as_dataframe : bool, optional
            Whether to return results as a Pandas DataFrame, by default True

        Returns
        -------
        Union[List[Dict[str, Any]], pd.DataFrame]
            The results as either a list of dictionaries or a Pandas DataFrame
        """

        return self._process_request(
            key_name="node_multi_label_counts",
            query_function=queries.get_node_multi_label_counts,
            refresh=refresh,
            as_dataframe=as_dataframe,
        )

    def node_properties(
        self, refresh: bool = False, as_dataframe: bool = True
    ) -> Union[List[Dict[str, Any]], pd.DataFrame]:
        """
        Get the properties for each unique node label in the graph.

        Parameters
        ----------
        refresh : bool, optional
            Whether to re-query the databae, by default False
        as_dataframe : bool, optional
            Whether to return results as a Pandas DataFrame, by default True

        Returns
        -------
        Union[List[Dict[str, Any]], pd.DataFrame]
            The results as either a list of dictionaries or a Pandas DataFrame
        """

        return self._process_request(
            key_name="node_properties",
            query_function=queries.get_node_properties,
            refresh=refresh,
            as_dataframe=as_dataframe,
        )

    def relationship_count(self, refresh: bool = False) -> int:
        """
        Count the total number of relationships in the graph.

        Parameters
        ----------
        refresh : bool, optional
            Whether to re-query the databae, by default False

        Returns
        -------
        int
            The number of relationships
        """

        response = self._process_request(
            key_name="relationship_count",
            query_function=queries.get_relationship_count,
            refresh=refresh,
            as_dataframe=False,
        )

        assert isinstance(response, int), "invalid response."

        return response

    def relationship_type_counts(
        self, refresh: bool = False, as_dataframe: bool = True
    ) -> Union[List[Dict[str, Any]], pd.DataFrame]:
        """
        Count the number of relationships in the graph by
        each unique relationship type.

        Parameters
        ----------
        refresh : bool, optional
            Whether to re-query the databae, by default False
        as_dataframe : bool, optional
            Whether to return results as a Pandas DataFrame, by default True

        Returns
        -------
        Union[List[Dict[str, Any]], pd.DataFrame]
            The results as either a list of dictionaries or a Pandas DataFrame
        """

        return self._process_request(
            key_name="relationship_type_counts",
            query_function=queries.get_relationship_type_counts,
            refresh=refresh,
            as_dataframe=as_dataframe,
        )

    def relationship_properties(
        self, refresh: bool = False, as_dataframe: bool = True
    ) -> Union[List[Dict[str, Any]], pd.DataFrame]:
        """
        Get the properties for each unique relationship type in the graph.

        Parameters
        ----------
        refresh : bool, optional
            Whether to re-query the databae, by default False
        as_dataframe : bool, optional
            Whether to return results as a Pandas DataFrame, by default True

        Returns
        -------
        Union[List[Dict[str, Any]], pd.DataFrame]
            The results as either a list of dictionaries or a Pandas DataFrame
        """

        return self._process_request(
            key_name="relationship_properties",
            query_function=queries.get_relationship_properties,
            refresh=refresh,
            as_dataframe=as_dataframe,
        )

    def unlabeled_node_count(self, refresh: bool = False) -> int:
        """
        Count the number of nodes in the graph that do not have labels.

        Parameters
        ----------
        refresh : bool, optional
            Whether to re-query the databae, by default False

        Returns
        -------
        int
            The number of unlabeled nodes
        """

        response = self._process_request(
            key_name="unlabeled_node_count",
            query_function=queries.get_unlabeled_node_count,
            refresh=refresh,
            as_dataframe=False,
        )

        assert isinstance(response, int), "invalid response."

        return response

    # identify unlabeled nodes
    def unlabeled_node_ids(
        self, refresh: bool = False, as_dataframe: bool = True
    ) -> Union[List[Dict[str, Any]], pd.DataFrame]:
        return self._process_request(
            key_name="unlabeled_node_ids",
            query_function=queries.get_unlabeled_node_ids,
            refresh=refresh,
            as_dataframe=as_dataframe,
        )

    def disconnected_node_count_by_label(
        self, refresh: bool = False, as_dataframe: bool = True
    ) -> Union[List[Dict[str, Any]], pd.DataFrame]:
        """
        Count the number of disconnected nodes by label in the graph.

        Parameters
        ----------
        refresh : bool, optional
            Whether to re-query the databae, by default False
        as_dataframe : bool, optional
            Whether to return results as a Pandas DataFrame, by default True

        Returns
        -------
        Union[List[Dict[str, Any]], pd.DataFrame]
            The results as either a list of dictionaries or a Pandas DataFrame
        """

        return self._process_request(
            key_name="disconnected_node_count_by_label",
            query_function=queries.get_disconnected_node_count_by_label,
            refresh=refresh,
            as_dataframe=as_dataframe,
        )

    def disconnected_node_count(self, refresh: bool = False) -> int:
        """
        Count the number of disconnected nodes in the graph.

        Parameters
        ----------
        refresh : bool, optional
            Whether to re-query the databae, by default False

        Returns
        -------
        int
            The number of disconnected nodes
        """

        response = self._process_request(
            key_name="disconnected_node_count",
            query_function=queries.get_disconnected_node_count,
            refresh=refresh,
            as_dataframe=False,
        )

        assert isinstance(response, int), "invalid response."

        return response

    def disconnected_node_ids(
        self, refresh: bool = False, as_dataframe: bool = True
    ) -> Union[List[Dict[str, Any]], pd.DataFrame]:
        """
        Identify the node ids of disconnected nodes in the graph.

        Parameters
        ----------
        refresh : bool, optional
            Whether to re-query the databae, by default False
        as_dataframe : bool, optional
            Whether to return results as a Pandas DataFrame, by default True

        Returns
        -------
        Union[List[Dict[str, Any]], pd.DataFrame]
            The results as either a list of dictionaries or a Pandas DataFrame
        """

        return self._process_request(
            key_name="disconnected_node_ids",
            query_function=queries.get_disconnected_node_ids,
            refresh=refresh,
            as_dataframe=as_dataframe,
        )

    def node_degrees(
        self, refresh: bool = False, as_dataframe: bool = True
    ) -> Union[List[Dict[str, Any]], pd.DataFrame]:
        """
        Calculate the in-degree and out-degree of each node in the graph.

        Parameters
        ----------
        refresh : bool, optional
            Whether to re-query the databae, by default False
        as_dataframe : bool, optional
            Whether to return results as a Pandas DataFrame, by default True

        Returns
        -------
        Union[List[Dict[str, Any]], pd.DataFrame]
            The results as either a list of dictionaries or a Pandas DataFrame
        """
        return self._process_request(
            key_name="node_degrees",
            query_function=queries.get_node_degrees,
            refresh=refresh,
            as_dataframe=as_dataframe,
        )
