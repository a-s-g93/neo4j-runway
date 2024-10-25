from datetime import datetime
from typing import Literal

import pandas as pd

from neo4j_runway.database.neo4j import Neo4jGraph

from ..cache import EDACache
from . import formatters


def create_eda_report(
    graph: Neo4jGraph,
    eda_cache: EDACache,
    include_unlabeled_node_ids: bool = False,
    include_disconnected_node_ids: bool = False,
    include_node_degrees: bool = True,
    order_node_degrees_by: Literal["in", "out"] = "out",
    top_k_node_degrees: int = 5,
    save_file: bool = False,
    file_name: str = "eda_report.md",
) -> str:
    """
    Generate a report containing information from the `Neo4jGraph` and `EDACache`.
    The report may be output in Markdown format.

    Parameters
    ----------
    graph : Neo4jGraph
        The Neo4j graph object containing information about the database.
    eda_cache : EDACache
        The cache containing results from queries ran by the GraphEDA class.
    save_file : bool, optional
        Whether to save the file, by default False
    file_name : str, optional
        The file name, if saving the file, by default eda_report.md

    Returns
    -------
    str
        The report in string format.
    """

    report = f"""
# Runway EDA Report

## Database Information
{formatters.format_main_database_info(graph=graph)}

### Counts
{formatters.format_counts_table(cache=eda_cache)}

### Indexes
{formatters.format_table(eda_cache.get("database_indexes"))}

### Constraints
{formatters.format_table(eda_cache.get("database_constraints"))}

## Nodes Overview
{formatters.format_node_overview(cache=eda_cache)}

## Relationships Overview
{formatters.format_relationship_overview(cache=eda_cache)}

{formatters.format_unlabled_node_ids(cache=eda_cache, include_unlabeled_node_ids=include_unlabeled_node_ids)}
{formatters.format_disconnected_node_ids(cache=eda_cache, include_disconnected_node_ids=include_disconnected_node_ids)}
{formatters.format_node_degrees(cache=eda_cache, include_node_degrees=include_disconnected_node_ids, order_node_degrees_by=order_node_degrees_by, top_k_node_degrees=top_k_node_degrees)}
---

Runway v{formatters.get_package_version()}

Report Generated @ {datetime.now()}
"""

    return report
