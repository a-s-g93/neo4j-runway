"""
The GraphEDA Queries module contains queries that return
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

from typing import Any, Dict, List

from neo4j import Driver


def get_database_indexes(
    driver: Driver, database: str = "neo4j"
) -> List[Dict[str, Any]]:
    """
    Method to identify the Neo4j database's indexes.

    Parameters
    ----------
    driver : Driver
        The Neo4j Driver to handle connections
    database : str, optional
        The Neo4j database name to connect to, by default neo4j

    Returns
    -------
    List[Dict[str, Any]]
        The results are a list of dictionaries, where each dictionary contains the index
        name as "name" and the list of labels for that index as "labels".
    """

    query = """SHOW INDEXES"""

    try:
        with driver.session(database=database) as session:
            response = session.run(query)
            return [record.data() for record in response]

    except Exception:
        driver.close()
        return [{}]


def get_database_constraints(
    driver: Driver, database: str = "neo4j"
) -> List[Dict[str, Any]]:
    """
    Get the constraints for the graph database.

    Parameters
    ----------
    driver : Driver
        The Neo4j Driver to handle connections
    database : str, optional
        The Neo4j database name to connect to, by default neo4j

    Returns
    -------
    List[Dict[str, Any]]
        The results are list of dictionaries, where each dictionary contains the
        constraint name as "name" and the list of labels for that constraint as "labels".
    """

    query = """SHOW CONSTRAINTS"""

    try:
        with driver.session(database=database) as session:
            response = session.run(query)
            return [record.data() for record in response]

    except Exception:
        driver.close()
        return [{}]


def get_node_count(driver: Driver, database: str = "neo4j") -> int:
    """
    Count the total number of nodes in the graph.

    Parameters
    ----------
    driver : Driver
        The Neo4j Driver to handle connections
    database : str, optional
        The Neo4j database name to connect to, by default neo4j

    Returns
    -------
    int
        This result is the count of nodes in the graph.
    """

    query = """MATCH (n) RETURN COUNT(n) AS nodeCount"""

    try:
        with driver.session(database=database) as session:
            response = session.run(query)
            response_list = [record.data() for record in response]
            return response_list[0]["nodeCount"]  # type: ignore[no-any-return]

    except Exception:
        driver.close()
        return -1


def get_node_label_counts(
    driver: Driver, database: str = "neo4j"
) -> List[Dict[str, Any]]:
    """
    Count the number of nodes associated with each
    unique label in the graph.

    Parameters
    ----------
    driver : Driver
        The Neo4j Driver to handle connections
    database : str, optional
        The Neo4j database name to connect to, by default neo4j

    Returns
    -------
    List[Dict[str, Any]]
        The results are a list of dictionaries, where each dictionary contains
        the unique node label in the database as "label" along with the
        corresponding node count as "count".
    """

    query = """MATCH (n)
                WITH n, labels(n) AS node_labels
                WITH node_labels[0] AS uniqueLabels
                RETURN uniqueLabels AS label, COUNT(uniqueLabels) AS count
                ORDER BY count DESC"""

    try:
        with driver.session(database=database) as session:
            response = session.run(query)
            return [record.data() for record in response]

    except Exception:
        driver.close()
        return [{}]


def get_node_multi_label_counts(
    driver: Driver, database: str = "neo4j"
) -> List[Dict[str, Any]]:
    """
    Identify nodes in the graph that have multiple labels.

    Parameters
    ----------
    driver : Driver
        The Neo4j Driver to handle connections
    database : str, optional
        The Neo4j database name to connect to, by default neo4j

    Returns
    -------
    List[Dict[str, Any]]
        The results are a list of dictionaries, where each dictionary contains
        the node id as "node_id" and the list of labels for that node as "labels".
    """

    query = """MATCH (n)
                WITH n, labels(n) as node_labels
                WHERE size(node_labels) > 1
                WITH node_labels as labelCombinations
                RETURN labelCombinations, count(labelCombinations) as nodeCount
                ORDER BY nodeCount DESC"""

    try:
        with driver.session(database=database) as session:
            response = session.run(query)
            return [record.data() for record in response]

    except Exception:
        driver.close()
        return [{}]


def get_node_properties(
    driver: Driver, database: str = "neo4j"
) -> List[Dict[str, Any]]:
    """
    Get the properties for each unique node label in the graph.

    Parameters
    ----------
    driver : Driver
        The Neo4j Driver to handle connections
    database : str, optional
        The Neo4j database name to connect to, by default neo4j

    Returns
    -------
    List[Dict[str, Any]]
        The results are a list of dictionaries, where each dictionary contains
        the unique node label in the database as "label" along with the list of
        properties for that label as "properties".
    """

    query = """CALL db.schema.nodeTypeProperties()"""

    try:
        with driver.session(database=database) as session:
            response = session.run(query)
            response_list = [record.data() for record in response]

            # remove the "nodeType" key from each dictionary and append to cache
            response_list = [
                {k: v for k, v in record.items() if k != "nodeType"}
                for record in response_list
            ]
            return response_list

    except Exception:
        driver.close()
        return [{}]


def get_relationship_count(driver: Driver, database: str = "neo4j") -> int:
    """
    Count the total number of relationships in the graph.

    Parameters
    ----------
    driver : Driver
        The Neo4j Driver to handle connections
    database : str, optional
        The Neo4j database name to connect to, by default neo4j

    Returns
    -------
    int
        This result is an integer representing the number of relationships
        in the graph.
    """

    query = """MATCH ()-[r]->() RETURN COUNT(r) AS relCount"""

    try:
        with driver.session(database=database) as session:
            response = session.run(query)
            response_list = [record.data() for record in response]
            return response_list[0]["relCount"]  # type: ignore[no-any-return]

    except Exception:
        driver.close()
        return -1


def get_relationship_type_counts(
    driver: Driver, database: str = "neo4j"
) -> List[Dict[str, Any]]:
    """
    Count the number of relationships in the graph by
    each unique relationship type.

    Parameters
    ----------
    driver : Driver
        The Neo4j Driver to handle connections
    database : str, optional
        The Neo4j database name to connect to, by default neo4j

    Returns
    -------
    List[Dict[str, Any]]
        The results are a list of dictionaries, where each dictionary contains
        the unique relationship type in the database as "label" along with the
        corresponding count as "count".
    """

    query = """MATCH ()-[r]->()
                WITH type(r) AS rel_type
                RETURN rel_type as relType, COUNT(rel_type) AS count
                ORDER BY count DESC"""

    try:
        with driver.session(database=database) as session:
            response = session.run(query)
            return [record.data() for record in response]

    except Exception:
        driver.close()
        return [{}]


def get_relationship_properties(
    driver: Driver, database: str = "neo4j"
) -> List[Dict[str, Any]]:
    """
    Get the properties for each unique relationship type in the graph.

    Parameters
    ----------
    driver : Driver
        The Neo4j Driver to handle connections
    database : str, optional
        The Neo4j database name to connect to, by default neo4j

    Returns
    -------
    List[Dict[str, Any]]
        The results are a of dictionaries, where each dictionary contains
        the unique relationship property name, property data type, and whether
        or not the relationship property is required by the schema.
    """

    query = """CALL db.schema.relTypeProperties()"""

    try:
        with driver.session(database=database) as session:
            response = session.run(query)
            response_list = [record.data() for record in response]

            # remove the "relationshipType" key from each dictionary
            response_list = [
                {k: v for k, v in record.items() if k != "relType"}
                for record in response_list
                if record["propertyName"] is not None
            ]

            return response_list

    except Exception:
        driver.close()
        return [{}]


def get_unlabeled_node_count(driver: Driver, database: str = "neo4j") -> int:
    """
    Count the number of nodes in the graph that do not have labels.

    Parameters
    ----------
    driver : Driver
        The Neo4j Driver to handle connections
    database : str, optional
        The Neo4j database name to connect to, by default neo4j

    Returns
    -------
    int
        The count of unlabeled nodes in the graph
    """

    query = """MATCH (n)
                WHERE labels(n) = []
                RETURN COUNT(n) AS unlabeled_ct"""

    try:
        with driver.session(database=database) as session:
            response = session.run(query)
            response_list = [record.data() for record in response]
            return response_list[0]["unlabeled_ct"]  # type: ignore[no-any-return]

    except Exception:
        driver.close()
        return -1


def get_unlabeled_node_ids(
    driver: Driver, database: str = "neo4j"
) -> List[Dict[str, Any]]:
    query = """MATCH (n)
                WHERE labels(n) = []
                RETURN ID(n) as ids"""

    try:
        with driver.session(database=database) as session:
            response = session.run(query)
            return [record.data() for record in response]

    except Exception:
        driver.close()
        return [{}]


def get_disconnected_node_count_by_label(
    driver: Driver, database: str = "neo4j"
) -> List[Dict[str, Any]]:
    """
    Count the number of disconnected nodes by label in the graph.

    Parameters
    ----------
    driver : Driver
        The Neo4j Driver to handle connections
    database : str, optional
        The Neo4j database name to connect to, by default neo4j

    Returns
    -------
    List[Dict[str, Any]]
        The results as a list of dictionaries, where each dictionary
        includes a node label and the count of disconnected nodes for that label
        ex: [{'nodeLabel': 'Customer', 'count': 2}]
    """

    query = """MATCH (n)
                WHERE NOT (n)--()
                WITH n, labels(n) as node_labels
                WITH node_labels[0] as nodeLabel
                RETURN nodeLabel, count(nodeLabel) as count
                ORDER BY count DESC"""

    try:
        with driver.session(database=database) as session:
            response = session.run(query=query)
            response_list = [record.data() for record in response]
            return response_list

    except Exception:
        driver.close()
        return [{}]


def get_disconnected_node_count(driver: Driver, database: str = "neo4j") -> int:
    """
    Count the number of disconnected nodes in the graph.

    Parameters
    ----------
    driver : Driver
        The Neo4j Driver to handle connections
    database : str, optional
        The Neo4j database name to connect to, by default neo4j

    Returns
    -------
    int
        The number of disconnected nodes
    """

    query = """MATCH (n)
                WHERE NOT (n)--()
                return count(n) as numDisconnected"""

    try:
        with driver.session(database=database) as session:
            response = session.run(query=query)
            response_list = [record.data() for record in response]
            return response_list[0]["numDisconnected"]  # type: ignore[no-any-return]

    except Exception:
        driver.close()
        return -1


def get_disconnected_node_ids(
    driver: Driver, database: str = "neo4j"
) -> List[Dict[str, Any]]:
    """
    Identify the node ids of disconnected nodes in the graph.

    Parameters
    ----------
    driver : Driver
        The Neo4j Driver to handle connections
    database : str, optional
        The Neo4j database name to connect to, by default neo4j

    Returns
    -------
    List[Dict[str, Any]]
        A list of dictionaries, where each dictionary contains the node label as "nodeLabel" and
        the node id as "node_id" for each disconnected node in the graph.
        ex: [{'nodeLabel': 'Customer', 'nodeId': 135}, {'nodeLabel': 'Customer', 'nodeId': 170}]
    """

    query = """MATCH (n)
                WHERE NOT (n)--()
                RETURN labels(n)[0] as nodeLabel, ID(n) as nodeId"""

    try:
        with driver.session(database=database) as session:
            response = session.run(query)
            response_list = [record.data() for record in response]
            return response_list

    except Exception:
        driver.close()
        return [{}]


############################
# GRAPH STATISTICS FUNCTIONS
############################


def get_node_degrees(driver: Driver, database: str = "neo4j") -> List[Dict[str, Any]]:
    """
    Calculate the in-degree and out-degree of each node in the graph.

    Parameters
    ----------
    driver : Driver
        The Neo4j Driver to handle connections
    database : str, optional
        The Neo4j database name to connect to, by default neo4j

    Returns
    -------
    List[Dict[str, Any]]
        A list of dictionaries, where each dictionary contains the node id as "nodeId",
        label as the "nodeLabel", the in-degree of the node as "inDegree", and the out-degree of
        the node as "outDegree".
    """

    query = """MATCH (n)
                OPTIONAL MATCH (n)-[r_out]->()
                WITH n, id(n) AS nodeId, labels(n) AS nodeLabel, count(r_out) AS outDegree
                OPTIONAL MATCH (n)<-[r_in]-()
                RETURN nodeId, nodeLabel, count(r_in) AS inDegree, outDegree
                ORDER BY outDegree DESC;
                """

    try:
        with driver.session(database=database) as session:
            response = session.run(query)
            return [record.data() for record in response]

    except Exception:
        driver.close()
        return [{}]
