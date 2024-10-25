from typing import Any, Dict, List, Optional, TypedDict


class EDACache(TypedDict):
    """
    The cache used to contain results from the GraphEDA module.

    Attributes
    ----------
    database_indexes : List[Dict[str, Any]]
        The database indexes as a list of maps containing id, name, state, populatoinPercent, type, entityType, labelsOrTypes, properties, indexProvider, owningConstraint, lastRead, readCount
    database_constraints : List[Dict[str, Any]]
        The database constraints as a list of maps containing id, name, type, entityType, labelsOrTypes, properties, ownedIndex, propertyType
    node_count : int
        The number of nodes in the database
    node_label_counts : List[Dict[str, Any]]
        List of maps containing label, count
    node_multi_label_counts : List[Dict[str, Any]]
        List of maps containing labelCombinations, nodeCounts
    node_properties : List[Dict[str, Any]]
        List of maps containing nodeLabels, propertyName, propertyTypes, mandatory
    relationship_count : int
        The number of relationships in the database
    relationship_type_counts : List[Dict[str, Any]]
        List of maps containing relType, count
    relationship_properties : List[Dict[str, Any]]
        List of maps containing propertyName, propertyTypes, mandatory
    unlabeled_node_count : List[Dict[str, Any]]
        The number of unlabeled nodes in the database
    unlabeled_node_ids : List[Dict[str, Any]]
        List of maps containing nodeId
    disconnected_node_count : int
        The disconnected node count
    disconnected_node_count_by_label : List[Dict[str, Any]]
        List of maps containing nodeLabel, count
    disconnected_node_ids : List[Dict[str, Any]]
        List of maps containing nodeLabel, nodeId
    node_degrees : List[Dict[str, Any]]
        List of maps containing nodeId, nodeLabel, inDegree, outDegree
    """

    database_indexes: Optional[List[Dict[str, Any]]]
    database_constraints: Optional[List[Dict[str, Any]]]
    node_count: Optional[int]
    node_label_counts: Optional[List[Dict[str, Any]]]
    node_multi_label_counts: Optional[List[Dict[str, Any]]]
    node_properties: Optional[List[Dict[str, Any]]]
    relationship_count: Optional[int]
    relationship_type_counts: Optional[List[Dict[str, Any]]]
    relationship_properties: Optional[List[Dict[str, Any]]]
    unlabeled_node_count: Optional[int]
    unlabeled_node_ids: Optional[List[Dict[str, Any]]]
    disconnected_node_count: Optional[int]
    disconnected_node_count_by_label: Optional[List[Dict[str, Any]]]
    disconnected_node_ids: Optional[List[Dict[str, Any]]]
    node_degrees: Optional[List[Dict[str, Any]]]


def create_eda_cache() -> EDACache:
    """
    Initialize a fresh EDACache

    Returns
    -------
    EDACache
        The cache
    """

    return EDACache(
        database_indexes=None,
        database_constraints=None,
        node_count=None,
        node_label_counts=None,
        node_multi_label_counts=None,
        node_properties=None,
        relationship_count=None,
        relationship_type_counts=None,
        relationship_properties=None,
        unlabeled_node_count=None,
        unlabeled_node_ids=None,
        disconnected_node_count=None,
        disconnected_node_count_by_label=None,
        disconnected_node_ids=None,
        node_degrees=None,
    )
