from typing import Any, Dict, List, Literal, Optional

import pandas as pd

from neo4j_runway import __version__ as package_version
from neo4j_runway.database.neo4j import Neo4jGraph

from ..cache import EDACache


def get_package_version() -> str:
    return package_version


def format_main_database_info(graph: Neo4jGraph) -> str:
    data = [
        {
            "databaseName": graph.database,
            "databaseVersion": graph.database_version,
            "databaseEdition": graph.database_edition,
            "APOCVersion": graph.apoc_version or "not installed",
            "GDSVersion": graph.gds_version or "not installed",
        }
    ]
    return format_table(data)


def format_counts_table(cache: EDACache) -> str:
    data = [
        {
            "nodeCount": cache.get("node_count"),
            "unlabeledNodeCount": cache.get("unlabeled_node_count"),
            "disconnectedNodeCount": cache.get("disconnected_node_count"),
            "relationshipCount": cache.get("relationship_count"),
        }
    ]

    return format_table(data)


def format_table(data: Optional[List[Dict[str, Any]]]) -> str:
    if data is not None:
        return pd.DataFrame(data).to_markdown()  # type: ignore[no-any-return]
    return ""


def format_node_degrees_table(
    data: List[Dict[str, Any]],
    order_node_degrees_by: Literal["in", "out"],
    top_k_node_degrees: int,
) -> str:
    df = pd.DataFrame(data).sort_values(
        by=order_node_degrees_by + "Degree", ascending=False
    )
    return df.head(top_k_node_degrees).to_markdown()  # type: ignore[no-any-return]


def format_node_overview(cache: EDACache) -> str:
    report = ""
    if content := cache.get("node_label_counts"):
        report += f"### Label Counts\n{format_table(content)}\n"

    if content := cache.get("node_multi_label_counts"):
        report += f"### Multi-Label Counts\n{format_table(content)}\n"

    if content := cache.get("node_properties"):
        report += f"### Properties\n{format_table(content)}\n"

    return report


def format_relationship_overview(cache: EDACache) -> str:
    report = ""

    if content := cache.get("relationship_type_counts"):
        report += f"### Type Counts\n{format_table(content)}\n"

    if content := cache.get("relationship_properties"):
        report += f"### Properties\n{format_table(content)}\n"
    else:
        report += f"### Properties\nno relationship properties\n"

    return report


def format_unlabled_node_ids(cache: EDACache, include_unlabeled_node_ids: bool) -> str:
    if not include_unlabeled_node_ids:
        return ""

    if content := cache.get("unlabeled_node_ids"):
        return f"## Unlabeled Nodes\n{format_table(content)}"
    else:
        return f"## Unlabeled Nodes\nno unlabeled nodes data in cache"


def format_disconnected_node_ids(
    cache: EDACache, include_disconnected_node_ids: bool
) -> str:
    if not include_disconnected_node_ids:
        return ""

    if content := cache.get("disconnected_node_ids"):
        return f"## Disconnected Nodes\n{format_table(content)}"
    else:
        return f"## Disconnected Nodes\nno disconnected nodes data in cache"


def format_node_degrees(
    cache: EDACache,
    include_node_degrees: bool,
    order_node_degrees_by: Literal["in", "out"],
    top_k_node_degrees: int,
) -> str:
    if not include_node_degrees:
        return ""

    if content := cache.get("node_degrees"):
        return f"""## Node Degrees
* Top {top_k_node_degrees} Ordered By {order_node_degrees_by}Degree

{format_node_degrees_table(content, order_node_degrees_by=order_node_degrees_by, top_k_node_degrees=top_k_node_degrees)}"""
    else:
        return f"## Node Degrees\nno node degrees data in cache"
