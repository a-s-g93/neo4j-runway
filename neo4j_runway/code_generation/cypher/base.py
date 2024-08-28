"""
This file contains the functions to create MATCH, MERGE and SET queries.
"""

from typing import List, Optional

from ...exceptions import LoadCSVCypherGenerationError
from ...models import Node, Property, Relationship


def generate_match_node_clause(node: Node, use_alias: bool = False) -> str:
    """
    Generate a MATCH node clause.
    """

    if use_alias and (node.node_key_aliases or node.unique_property_aliases):
        set_clause = generate_set_unique_property_aliases(
            node.node_key_aliases or node.unique_property_aliases
        )
    else:
        set_clause = generate_set_unique_property(
            node.node_keys or node.unique_properties
        )

    return "MATCH (n:" + node.label + " {" + f"{set_clause}" + "})"


def generate_match_same_node_labels_clause(node: Node) -> str:
    """
    Generate the two match statements for node with two unique csv mappings.
    This is used when a relationship connects two nodes with the same label.
    An example: (:Person{name: row.person_name})-[:KNOWS]->(:Person{name:row.knows_person})
    """
    from_unique, to_unique = [
        [
            "{" + f"{prop.name}: row.{prop.column_mapping}" + "}",
            "{" + f"{prop.name}: row.{prop.alias}" + "}",
        ]
        for prop in node.unique_properties
        if prop.alias is not None
    ][0]

    return f"""MATCH (source:{node.label} {from_unique})
MATCH (target:{node.label} {to_unique})"""


def generate_set_property(
    properties: List[Property], strict_typing: bool = True
) -> str:
    """
    Generate a set property string.
    """

    temp_set_list = []

    for prop in properties:
        temp_set_list.append(f"n.{prop.name} = {cast_value(prop, strict_typing)}")

    result = ", ".join(temp_set_list)

    if not result == "":
        result = f"SET {result}"

    return result


def generate_set_unique_property(
    unique_properties: List[Property], strict_typing: bool = True
) -> str:
    """
    Generate the unique properties to match a node on within a MERGE statement.
    Returns: unique_property_match_component
    """

    res = [
        f"{prop.name}: {cast_value(prop, strict_typing)}" for prop in unique_properties
    ]
    return ", ".join(res)


def generate_set_unique_property_aliases(
    unique_properties: List[Property], strict_typing: bool = True
) -> str:
    """
    Generate the unique properties to match a node on within a MERGE statement.
    Will use alias names from files.
    Returns: unique_property_match_component
    """

    res = [
        f"{prop.name}: {cast_value(prop, strict_typing, use_alias=True)}"
        for prop in unique_properties
    ]
    return ", ".join(res)


def generate_merge_node_clause_standard(node: Node, strict_typing: bool = True) -> str:
    """
    Generate a MERGE node clause.
    """

    return f"""WITH $dict.rows AS rows
UNWIND rows AS row
MERGE (n:{node.label} {{{generate_set_unique_property(node.node_keys or node.unique_properties, strict_typing)}}})
{generate_set_property(node.nonidentifying_properties, strict_typing)}"""


def generate_merge_node_load_csv_clause(
    source_name: str,
    method: str = "api",
    batch_size: int = 10000,
    node: Optional[Node] = None,
    standard_clause: Optional[str] = None,
    strict_typing: bool = True,
) -> str:
    """
    Generate a MERGE node clause for the LOAD CSV method.
    """

    if not node and not standard_clause:
        raise ValueError("Either `node` or `standard_clause` arg must be provided!")

    command = ":auto " if method == "browser" else ""
    if not standard_clause and node is not None:
        standard_clause = generate_merge_node_clause_standard(
            node=node, strict_typing=strict_typing
        )
    if standard_clause is not None:
        standard_clause = (
            standard_clause.strip().split("\n", 2)[2].replace("\n", "\n    ")
        )
    else:
        raise LoadCSVCypherGenerationError(
            "Unable to construct MERGE node clause for LOAD CSV from provided arguments."
        )

    return f"""{command}LOAD CSV WITH HEADERS FROM 'file:///{source_name}' as row
CALL {{
    WITH row
    {standard_clause.strip()}
}} IN TRANSACTIONS OF {str(batch_size)} ROWS;
"""


def generate_merge_relationship_clause_standard(
    relationship: Relationship,
    source_node: Node,
    target_node: Node,
    strict_typing: bool = True,
) -> str:
    """
    Generate a MERGE relationship clause.
    """

    use_source_alias: bool = bool(
        relationship.source_name and relationship.source_name != source_node.source_name
    )
    use_target_alias: bool = bool(
        relationship.source_name and relationship.source_name != target_node.source_name
    )

    if source_node.label == target_node.label:
        return f"""WITH $dict.rows AS rows
UNWIND rows as row
{generate_match_same_node_labels_clause(node=source_node)}
MERGE (source)-[n:{relationship.type}]->(target)
{generate_set_property(relationship.nonidentifying_properties, strict_typing)}"""
    else:
        return f"""WITH $dict.rows AS rows
UNWIND rows as row
{generate_match_node_clause(source_node, use_alias=use_source_alias).replace('(n:', '(source:')}
{generate_match_node_clause(target_node, use_alias=use_target_alias).replace('(n:', '(target:')}
MERGE (source)-[n:{relationship.type}]->(target)
{generate_set_property(relationship.nonidentifying_properties, strict_typing)}"""


def generate_merge_relationship_load_csv_clause(
    source_name: str,
    method: str = "api",
    batch_size: int = 10000,
    relationship: Optional[Relationship] = None,
    source_node: Optional[Node] = None,
    target_node: Optional[Node] = None,
    standard_clause: Optional[str] = None,
    strict_typing: bool = True,
) -> str:
    """
    Generate a MERGE relationship clause for the LOAD CSV method.
    """
    if (not relationship or not source_node or not target_node) and not standard_clause:
        raise ValueError(
            "Either (`relationship`, `source_node` and `target_node`) or `standard_clause` arg must be provided!"
        )

    command = ":auto " if method == "browser" else ""
    if (
        not standard_clause
        and relationship is not None
        and source_node is not None
        and target_node is not None
    ):
        standard_clause = generate_merge_relationship_clause_standard(
            relationship=relationship,
            source_node=source_node,
            target_node=target_node,
            strict_typing=strict_typing,
        )
    if standard_clause is not None:
        standard_clause = (
            standard_clause.strip().split("\n", 2)[2].replace("\n", "\n    ")
        )
    else:
        raise LoadCSVCypherGenerationError(
            "Unable to construct MERGE relationship clause for LOAD CSV from provided arguments."
        )
    return f"""{command}LOAD CSV WITH HEADERS FROM 'file:///{source_name}' as row
CALL {{
    WITH row
    {standard_clause.strip()}
}} IN TRANSACTIONS OF {str(batch_size)} ROWS;
"""


def cast_value(
    prop: Property, strict_typing: bool = True, use_alias: bool = False
) -> str:
    """
    format property to be cast to correct type during ingestion.
    """

    # take the first val as this is the identifying column
    # column_mapping = (
    #     prop.column_mapping[0] if isinstance(prop.column_mapping, list) else prop.column_mapping
    # )

    column_mapping = prop.column_mapping if not use_alias else prop.alias

    assert (
        column_mapping is not None
    ), f"`column_mapping` can not be None. Found on Property {prop}"
    # escape bad chars
    column_mapping = (
        f"`{column_mapping}`"
        if not column_mapping[0].isalnum() or " " in column_mapping
        else column_mapping
    )

    base = f"row.{column_mapping}"

    if not strict_typing:
        return base

    if prop.type.lower().endswith("date"):
        return f"date({base})"
    elif prop.type.lower().endswith("datetime"):
        return f"datetime({base})"
    elif prop.type.lower().endswith("time"):
        return f"time({base})"
    elif prop.type.lower().endswith("point"):
        return f"point({base})"
    elif prop.type.lower().endswith("int"):
        return f"toIntegerOrNull({base})"
    elif prop.type.lower().endswith("float"):
        return f"toFloatOrNull({base})"
    elif prop.type.lower().endswith("bool"):
        return f"toBooleanOrNull({base})"
    else:
        return base
