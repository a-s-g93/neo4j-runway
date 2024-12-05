---
permalink: /api/graph-eda/graph-eda/
title: GraphEDA
toc: true
toc_label: GraphEDA
toc_icon: "fa-solid fa-plane"
---

    from neo4j_runway.graph_eda import GraphEDA



  The GraphEDA module contains queries that return
 information about the Neo4j database and its contents.

 The purpose of GraphEDA is to understand the
        characteristics
 of the data in graph form (nodes, relationships, and
        properties).
 This also helps identify errors and outliers in the data.

 The methods in this class primarily use Cypher to query and
        analyze
 data in the graph. The queries use Cypher because
        apoc.meta.schema
 uses sampling techniques and so the results are not
        necessarily deterministic.

 WARNING: The methods in this module can be computationally
        expensive.
 It is not recommended to use this module on massive Neo4j
        databases
 (i.e., nodes and relationships in the hundreds of millions)

    Attributes
    ----------

    database_version : str
        The database version
    database_edition : str
        The database edition
    report : str
        A report containing the results of EDA queries ran
        against the database



## Class Methods


### __init__
Initialize a GraphEDA class.

    Parameters
    ----------
    graph : Optional[Neo4jGraph], optional
        The `Neo4jGraph` object to be used to run queries.
        If not provided, will attempt to create via
        environment variables., by default None

    Raises
    ------
    ValueError
        If unable to construct `Neo4jGraph` object from
        environment variables.


### create_eda_report
Generate a report containing information from the
        `Neo4jGraph` and internal cache containing eda query
        results.
    The report may be output in Markdown format.

    Parameters
    ----------
    include_unlabeled_node_ids : bool, optional
        Whether to include the ids of unlabeled nodes, by
        default False
    include_disconnected_node_ids : bool, optional
        Whether to include the ids of disconnected nodes, by
        default False
    include_node_degrees : bool, optional
        Whether to include information on node degrees, by
        default True
    order_node_degrees_by : Literal["in", "out"], optional
        How to order the node degrees table, by default
        "out"
    top_k_node_degrees : int, optional
        How many rows to include in the node degrees table,
        by default 5
    save_file : bool, optional
        Whether to save the file, by default False
    file_name : str, optional
        The file name, if saving the file, by default
        eda_report.md
    view_report : bool, optional
        Whether to print the report upon completion, by
        default True
    notebook : bool, optional
        Whether the report will be displayed in a Python
        notebook, by default True
    return_report : bool, optional
        Whether to directly return the report as a String,
        by default True

    Returns
    -------
    Optional[str]
        The report in string format, if `return_report` is
        True


### database_constraints
Get the constraints for the graph database.

    Parameters
    ----------
    refresh : bool, optional
        Whether to re-query the databae, by default False
    as_dataframe : bool, optional
        Whether to return results as a Pandas DataFrame, by
        default True

    Returns
    -------
    Union[List[Dict[str, Any]], pd.DataFrame]
        The results as either a list of dictionaries or a
        Pandas DataFrame


### database_indexes
Method to identify the Neo4j database's indexes.

    Parameters
    ----------
    refresh : bool, optional
        Whether to re-query the databae, by default False
    as_dataframe : bool, optional
        Whether to return results as a Pandas DataFrame, by
        default True

    Returns
    -------
    Union[List[Dict[str, Any]], pd.DataFrame]
        The results as either a list of dictionaries or a
        Pandas DataFrame


### delete_cache
Delete the query result cache.


### disconnected_node_count
Count the number of disconnected nodes in the graph.

    Parameters
    ----------
    refresh : bool, optional
        Whether to re-query the databae, by default False

    Returns
    -------
    int
        The number of disconnected nodes


### disconnected_node_count_by_label
Count the number of disconnected nodes by label in the
        graph.

    Parameters
    ----------
    refresh : bool, optional
        Whether to re-query the databae, by default False
    as_dataframe : bool, optional
        Whether to return results as a Pandas DataFrame, by
        default True

    Returns
    -------
    Union[List[Dict[str, Any]], pd.DataFrame]
        The results as either a list of dictionaries or a
        Pandas DataFrame


### disconnected_node_ids
Identify the node ids of disconnected nodes in the
        graph.

    Parameters
    ----------
    refresh : bool, optional
        Whether to re-query the databae, by default False
    as_dataframe : bool, optional
        Whether to return results as a Pandas DataFrame, by
        default True

    Returns
    -------
    Union[List[Dict[str, Any]], pd.DataFrame]
        The results as either a list of dictionaries or a
        Pandas DataFrame


### node_count
Count the total number of nodes in the graph.

    Parameters
    ----------
    refresh : bool, optional
        Whether to re-query the databae, by default False

    Returns
    -------
    int
        The number of nodes


### node_degrees
Calculate the in-degree and out-degree of each node in
        the graph.

    Parameters
    ----------
    refresh : bool, optional
        Whether to re-query the databae, by default False
    as_dataframe : bool, optional
        Whether to return results as a Pandas DataFrame, by
        default True
    top_k : int, optional
        The top number of results to return, by default 10
    order_by : Literal['in', 'out'], optional
        Whether to order by inDegree or outDegree, by
        default 'out'

    Returns
    -------
    Union[List[Dict[str, Any]], pd.DataFrame]
        The results as either a list of dictionaries or a
        Pandas DataFrame


### node_label_counts
Count the number of nodes associated with each
    unique label in the graph.

    Parameters
    ----------
    refresh : bool, optional
        Whether to re-query the databae, by default False
    as_dataframe : bool, optional
        Whether to return results as a Pandas DataFrame, by
        default True

    Returns
    -------
    Union[List[Dict[str, Any]], pd.DataFrame]
        The results as either a list of dictionaries or a
        Pandas DataFrame


### node_multi_label_counts
Identify nodes in the graph that have multiple labels.

    Parameters
    ----------
    refresh : bool, optional
        Whether to re-query the databae, by default False
    as_dataframe : bool, optional
        Whether to return results as a Pandas DataFrame, by
        default True

    Returns
    -------
    Union[List[Dict[str, Any]], pd.DataFrame]
        The results as either a list of dictionaries or a
        Pandas DataFrame


### node_properties
Get the properties for each unique node label in the
        graph.

    Parameters
    ----------
    refresh : bool, optional
        Whether to re-query the databae, by default False
    as_dataframe : bool, optional
        Whether to return results as a Pandas DataFrame, by
        default True

    Returns
    -------
    Union[List[Dict[str, Any]], pd.DataFrame]
        The results as either a list of dictionaries or a
        Pandas DataFrame


### relationship_count
Count the total number of relationships in the graph.

    Parameters
    ----------
    refresh : bool, optional
        Whether to re-query the databae, by default False

    Returns
    -------
    int
        The number of relationships


### relationship_properties
Get the properties for each unique relationship type in
        the graph.

    Parameters
    ----------
    refresh : bool, optional
        Whether to re-query the databae, by default False
    as_dataframe : bool, optional
        Whether to return results as a Pandas DataFrame, by
        default True

    Returns
    -------
    Union[List[Dict[str, Any]], pd.DataFrame]
        The results as either a list of dictionaries or a
        Pandas DataFrame


### relationship_type_counts
Count the number of relationships in the graph by
    each unique relationship type.

    Parameters
    ----------
    refresh : bool, optional
        Whether to re-query the databae, by default False
    as_dataframe : bool, optional
        Whether to return results as a Pandas DataFrame, by
        default True

    Returns
    -------
    Union[List[Dict[str, Any]], pd.DataFrame]
        The results as either a list of dictionaries or a
        Pandas DataFrame


### run
Run all analytics on the database. Results will be added
        to the cache.
    WARNING: The methods in this module can be
        computationally expensive.
    It is not recommended to use this module on massive
        Neo4j databases
    (i.e., nodes and relationships in the hundreds of
        millions)

    Parameters
    ----------
    refresh : bool, optional
        Whether to refresh all analytics regardless of if
        they've been previously ran, by default False
    include : List[str], optional
        The methods to include. Overwrites any content in
        exclude. If `None`, then this arg is ignored, by
        default None
    exclude : List[str], optional
        The methods to exclude. If `None` or `include` is
        not `None`, then this arg is ignored, by default
        None
    return_cache : bool, optional
        Whether to directly return the updated cache, by
        default True
    method_params : Dict[str, Dict[str, Any]], optional
        Any parameters to include with method calls. Methods
        are keys and values are a dictionary of argument
        keys and values. By default dict()

    Returns
    -------
    Optional[EDACache]
        The results cache if `return_cache` is True


### save_report
Save the report to a Markdown file.

    Parameters
    ----------
    file_name : str, optional
        The file name, by default "eda_report.md"


### unlabeled_node_count
Count the number of nodes in the graph that do not have
        labels.

    Parameters
    ----------
    refresh : bool, optional
        Whether to re-query the databae, by default False

    Returns
    -------
    int
        The number of unlabeled nodes


### unlabeled_node_ids



### view_report
View the report.

    Parameters
    ----------
    notebook : bool, optional
        If viewing in a notebook setting, by default True



## Class Properties


### available_methods
The available methods to be run against the database.


### database_edition
The database edition


### database_version
The database version
