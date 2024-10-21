from typing import List, Literal

from graphviz import Digraph

from .node import Node
from .relationship import Relationship


def create_dot(
    nodes: List[Node],
    relationships: List[Relationship],
    detail_level: Literal[1, 2, 3] = 3,
    neo4j_typing: bool = False,
) -> Digraph:
    dot = Digraph(
        comment="Data Model",
        engine="dot",
        graph_attr={"pad": "0.5", "bgcolor": "azure"},
        node_attr={
            "shape": "oval",
            "color": "black",
            "style": "filled",
            "fillcolor": "azure3",
        },
        edge_attr={"labeldistance": "20.0", "penwidth": "2"},
    )

    for node in nodes:
        node_label = format_node(
            node=node, detail_level=detail_level, neo4j_typing=neo4j_typing
        )
        dot.node(name=node.label, label=node_label)

    for rel in relationships:
        rel_label = format_relationship(
            relationship=rel, detail_level=detail_level, neo4j_typing=neo4j_typing
        )
        dot.edge(
            tail_name=rel.source,
            head_name=rel.target,
            label=rel_label,
        )

    return dot


def format_node(
    node: Node, detail_level: Literal[1, 2, 3] = 3, neo4j_typing: bool = False
) -> str:
    """Format a node for Graphviz visual"""

    assert detail_level < 4 and detail_level > 0, "Detail level must be 1, 2 or 3"
    match detail_level:
        case 1:
            return f"\n(:{node.label})\n "
        case 2:
            schema = node.get_schema(verbose=False, neo4j_typing=neo4j_typing)
        case 3:
            schema = node.get_schema(verbose=True, neo4j_typing=neo4j_typing)

    parts = schema.split("\n")
    lbl = parts[0] + "\n"
    props = r"\l".join(parts[1:])

    return lbl + props


def format_relationship(
    relationship: Relationship,
    detail_level: Literal[1, 2, 3] = 3,
    neo4j_typing: bool = False,
) -> str:
    """Format a relationship for Graphviz visual"""

    assert detail_level < 4 and detail_level > 0, "Detail level must be 1, 2 or 3"
    match detail_level:
        case 1:
            return f"[:{relationship.type}]"
        case 2:
            schema = relationship.get_schema(verbose=False, neo4j_typing=neo4j_typing)
        case 3:
            schema = relationship.get_schema(verbose=True, neo4j_typing=neo4j_typing)

    parts = schema.split("\n")
    props = r"\l".join(parts[1:])
    return "  [:" + relationship.type + "]  " + "\n" + props
