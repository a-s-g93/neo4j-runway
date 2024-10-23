import logging
from typing import Any, Callable, Dict, List, Literal, Optional, Union

import dotenv
import pandas as pd

from ..database.neo4j import Neo4jGraph
from ..utils._utils.read_env import read_environment
from . import queries
from .cache import EDACache, create_eda_cache

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

    WARNING: The functions in this module can be computationally expensive.
    It is not recommended to use this module on massive Neo4j databases
    (i.e., nodes and relationships in the hundreds of millions)
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
                # import and read from .env file
                dotenv.load_dotenv()

                self.graph = Neo4jGraph(
                    username=read_environment("NEO4J_USERNAME"),
                    password=read_environment("NEO4J_PASSWORD"),
                    uri=read_environment("NEO4J_URI"),
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

    @property
    def database_version(self) -> str:
        """The database version"""
        return self.graph.database_version

    @property
    def database_edition(self) -> str:
        """The database edition"""
        return self.graph.database_edition

    def delete_cache(self) -> None:
        """
        Delete the query result cache.

        Parameters:
            None

        Returns:
            None
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

        Parameters:
            None

        Returns:
            None
            The method adds the query results to the cache dictionary.
            The results are a list of dictionaries, where each dictionary contains the index
            name as "name" and the list of labels for that index as "labels".
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

        Parameters:
            None

        Returns:
            None
            The method adds the query results to the cache dictionary.
            The results are list of dictionaries, where each dictionary contains the
            constraint name as "name" and the list of labels for that constraint as "labels".
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

        Parameters:
            None

        Returns:
            None
            The method adds the query results to the cache dictionary.
            This result is the count of nodes in the graph.
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

        Parameters:
            None

        Returns:
            None
            The method adds the query results to the cache dictionary.
            The results are a list of dictionaries, where each dictionary contains
            the unique node label in the database as "label" along with the
            corresponding node count as "count".
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

        Parameters:
            None

        Returns:
            None
            The method adds the query results to the cache dictionary.
            The results are a list of dictionaries, where each dictionary contains
            the node id as "node_id" and the list of labels for that node as "labels".
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

        Parameters:
            None

        Returns:
            None
            The method adds the query results to the cache dictionary.
            The results are a list of dictionaries, where each dictionary contains
            the unique node label in the database as "label" along with the list of
            properties for that label as "properties".
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

        Parameters:
            None

        Returns:
            None
            The method adds the query result to the cache dictionary.
            This result is an integer representing the number of relationships
            in the graph.
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

        Parameters:
            None

        Returns:
            None
            The method adds the query results to the cache dictionary.
            The results are a list of dictionaries, where each dictionary contains
            the unique relationship type in the database as "label" along with the
            corresponding count as "count".
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

        Parameters:
            None

        Returns:
            None
            The method adds the query results to the cache dictionary.
            The results are a of dictionaries, where each dictionary contains
            the unique relationship property name, property data type, and whether
            or not the relationship property is required by the schema.
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

        Parameters:
            None

        Returns:
            None

                The count of unlabeled nodes in the graph
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

    # count disconnected nodes
    def count_disconnected_nodes(
        self, refresh: bool = False, as_dataframe: bool = True
    ) -> Union[List[Dict[str, Any]], pd.DataFrame]:
        """
        Count the number of disconnected nodes in the graph.

        Parameters:
            None

        Returns:
            None


        - the results as a list of dictionaries, where each dictionary
        includes a node label and the count of disconnected nodes for that label
        - ex: [{'nodeLabel': 'Customer', 'count': 2}]
        - also appends the results to the cache dictionary
        """

        return self._process_request(
            key_name="disconnected_node_count",
            query_function=queries.get_disconnected_node_count,
            refresh=refresh,
            as_dataframe=as_dataframe,
        )

    # identify disconnected nodes
    def disconnected_node_ids(
        self, refresh: bool = False, as_dataframe: bool = True
    ) -> Union[List[Dict[str, Any]], pd.DataFrame]:
        """
        Identify the node ids of disconnected nodes in the graph.
        Parameters:
            None
        Returns:
            list: A list of dictionaries, where each dictionary contains the node label as "nodeLabel" and
            the node id as "node_id" for each disconnected node in the graph.
            ex: [{'nodeLabel': 'Customer', 'nodeId': 135}, {'nodeLabel': 'Customer', 'nodeId': 170}]
        """

        return self._process_request(
            key_name="disconnected_node_ids",
            query_function=queries.get_disconnected_node_ids,
            refresh=refresh,
            as_dataframe=as_dataframe,
        )

    def node_degree(
        self, refresh: bool = False, as_dataframe: bool = True
    ) -> Union[List[Dict[str, Any]], pd.DataFrame]:
        """
        Calculate the in-degree and out-degree of each node in the graph.
        Parameters:
            None
        Returns:
            list: A list of dictionaries, where each dictionary contains the node id as "node_id",
            label as the node label, the in-degree of the node as "inDegree", and the out-degree of
            the node as "outDegree".
        """
        return self._process_request(
            key_name="node_degrees",
            query_function=queries.get_node_degrees,
            refresh=refresh,
            as_dataframe=as_dataframe,
        )

    # def return_constraints(self) -> Union[str, pd.DataFrame]:
    #     """
    #     Calls GraphEDA.database_constraints().
    #     Formats the returned constrains into a pandas DataFrame for consumption and use.
    #     Parameters:
    #         None
    #     Returns:
    #         Prints output as either a string or pandas DataFrame
    #     """

    #     # call database_constraints() method to get the constrains
    #     db_constraints = self.graph_eda.database_constraints()

    #     # print output as string or pandas DataFrame
    #     if len(db_constraints) == 0:
    #         print("No constraints in database.")
    #     else:
    #         print(pd.DataFrame(db_constraints)
    #             .loc[:, ['name', 'type', 'entityType', 'labelsOrTypes', 'properties']]
    #             .to_string(index=False))

    # def run_database_eda(self, graph_eda):
    #     print("##########################################")
    #     print("# Neo4j Exploratory Data Analysis Report")
    #     print("##########################################")

    #     print("\n########## DATABASE DETAILS ##########")

    #     graph_eda.print_database_version()

    # result = graph_eda.database_indexes()


# if __name__ == "__main__":
#     run_grapheda = GraphEDA()
#     run_grapheda.run_database_eda()

# print("\nNode Indexes:")
# ctr = 0
# for item in result:
#     if item['entityType'] == 'NODE' and item['labelsOrTypes'] is not None:
#         ctr += 1
#         print(item['labelsOrTypes'], ":", item['properties'])
# print("Node Indexes Count:", ctr)

# print("\nRelationship Indexes:")
# ctr = 0
# for item in result:
#     if item['entityType'] == 'RELATIONSHIP' and item['labelsOrTypes'] is not None:
#         ctr += 1
#         print(item['labelsOrTypes'], ":", item['properties'])
# if ctr > 0:
#     print("Relationship Indexe Count:", ctr)
# else:
#     print("No relationship indexes in database.")


# ############################
# # DATA EXPLORATION FUNCTIONS
# ############################

# print("\n########## NODE DETAILS ##########")

# _ = graph_eda.node_count()
# print("\nTotal nodes in database:", graph_eda.cache["node_count"])

# _ = graph_eda.node_label_counts()
# print("\nNode counts by label:")
# for item in graph_eda.cache["node_label_counts"]:
#     print(item['label'], ":", item['count'])

# print('\nMulti-Label Nodes:')
# _ = graph_eda.multi_label_nodes()
# if len(_) == 0:
#     print("No multi-label nodes in graph")
# else:
#     print(graph_eda.cache["multi_label_nodes"])

# print('\nNode Properties:')
# _ = graph_eda.node_properties()
# print(pd.DataFrame(graph_eda.cache["node_properties"])
#       .sort_values(by='nodeLabels', ascending=True)
#       .to_string(index=False))

# print("\n########## RELATIONSHIP DETAILS ##########")

# _ = graph_eda.relationship_count()
# print("\nTotal relationships in database:", graph_eda.cache["relationship_count"])

# print("\nRelationship counts by type:")
# _ = graph_eda.relationship_type_counts()
# for item in graph_eda.cache["relationship_type_counts"]:
#     print(item['label'], ":", item['count'])

# print("\nRelationship Properties:")
# _ =  graph_eda.relationship_properties()
# print(pd.DataFrame(graph_eda.cache["relationship_properties"])
#       .dropna(subset=['propertyName'])
#       .to_string(index=False))

# ############################
# # DATA QUALITY FUNCTIONS
# ############################


# print("\n########## DATA QUALITY ##########")

# _ = graph_eda.unlabeled_node_count()
# if graph_eda.cache["unlabeled_node_count"] == 0:
#     print("\nAll nodes in database have labels.")
# else:
#     print("\nUnlabeled nodes in database:", graph_eda.cache["unlabeled_node_count"])


# _ = graph_eda.count_disconnected_nodes()
# print('\nCount of disconnected nodes by label:')
# for item in graph_eda.cache["disconnected_nodes"]:
#     print(item['nodeLabel'], ":", item['count'])

# _ = graph_eda.disconnected_node_ids()
# print('\nDisconnected node ids:')
# print(pd.DataFrame(graph_eda.cache["disconnected_node_ids"])
#       .to_string(index=False))
# # for item in graph_eda.cache["disconnected_node_ids"]:
# #     print(item['nodeLabel'], ":", item['node_id'])

# print("\n########## GRAPH STATISTICS ##########")

# _ = graph_eda.node_degree()

# print("\nDistribution of Node Out-Degrees:")
# print(pd.DataFrame(graph_eda.cache["node_degrees"])['outDegree']
#       .describe(percentiles=[0.25, 0.5, 0.75, 0.9, 0.95, 0.99])
#       .round(2)
#       )

# print("\nNodes with Highest Out-Degrees:")
# print(pd.DataFrame(graph_eda.cache["node_degrees"])
#                    .sort_values(by='outDegree', ascending=False)
#                    .head(5)
#                    .to_string(index=False))

# print("\nDistribution of Node In-Degrees:")
# print(pd.DataFrame(graph_eda.cache["node_degrees"])['inDegree']
#       .describe(percentiles=[0.25, 0.5, 0.75, 0.9, 0.95, 0.99])
#       .round(2)
#       )

# print("\nNodes with Highest In-Degrees:")
# print(pd.DataFrame(graph_eda.cache["node_degrees"])
#                    .sort_values(by='inDegree', ascending=False)
#                    .head(5)
#                    .to_string(index=False))
