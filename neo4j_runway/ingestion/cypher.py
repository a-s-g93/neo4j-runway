"""
This file contains the functions to create cypher queries.
"""

from typing import List, Union

from ..objects import Property, Node, Relationship


def generate_constraints_key(
    label_or_type: str, unique_property: Union[Property, List[Property]]
) -> str:
    """
    Generate the key for a unique or node key constraint.
    """
    if isinstance(unique_property, Property):
        return f"{label_or_type.lower()}_{unique_property.name.lower()}"
    else:
        return f"{label_or_type.lower()}_{'_'.join([x.name.lower() for x in unique_property])}"


def generate_constraint(label_or_type: str, unique_property: Property) -> str:
    """
    Generate a constrant string.
    """

    return f"CREATE CONSTRAINT {label_or_type.lower()}_{unique_property.name.lower()} IF NOT EXISTS FOR (n:{label_or_type}) REQUIRE n.{unique_property.name} IS UNIQUE;\n"


def generate_match_node_clause(node: Node) -> str:
    """
    Generate a MATCH node clause.
    """

    return (
        "MATCH (n:"
        + node.label
        + " {"
        + f"{generate_set_unique_property(node.node_keys or node.unique_properties)}"
        + "})"
    )


def generate_match_same_node_labels_clause(node: Node) -> str:
    """
    Generate the two match statements for node with two unique csv mappings.
    This is used when a relationship connects two nodes with the same label.
    An example: (:Person{name: row.person_name})-[:KNOWS]->(:Person{name:row.knows_person})
    """
    from_unique, to_unique = [
        [
            "{" + f"{prop.name}: row.{prop.csv_mapping}" + "}",
            "{" + f"{prop.name}: row.{prop.csv_mapping_other}" + "}",
        ]
        for prop in node.unique_properties
        if prop.csv_mapping_other is not None
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


def generate_merge_node_clause_standard(node: Node, strict_typing: bool = True) -> str:
    """
    Generate a MERGE node clause.
    """

    return f"""WITH $dict.rows AS rows
UNWIND rows AS row
MERGE (n:{node.label} {{{generate_set_unique_property(node.node_keys or node.unique_properties, strict_typing)}}})
{generate_set_property(node.nonidentifying_properties, strict_typing)}"""


def generate_merge_node_load_csv_clause(
    node: Node,
    csv_name: str,
    method: str = "api",
    batch_size: int = 10000,
    strict_typing: bool = True,
) -> str:
    """
    Generate a MERGE node clause for the LOAD CSV method.
    """

    command = ":auto " if method == "browser" else ""
    return f"""{command}LOAD CSV WITH HEADERS FROM 'file:///{csv_name}' as row
CALL {{
    WITH row
    MERGE (n:{node.label} {{{generate_set_unique_property(node.node_keys or node.unique_properties, strict_typing)}}})
    {generate_set_property(node.nonidentifying_properties, strict_typing)}
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
    if source_node.label == target_node.label:
        return f"""WITH $dict.rows AS rows
UNWIND rows as row
{generate_match_same_node_labels_clause(node=source_node)}
MERGE (source)-[n:{relationship.type}]->(target)
{generate_set_property(relationship.nonidentifying_properties, strict_typing)}"""
    else:
        return f"""WITH $dict.rows AS rows
UNWIND rows as row
{generate_match_node_clause(source_node).replace('(n:', '(source:')}
{generate_match_node_clause(target_node).replace('(n:', '(target:')}
MERGE (source)-[n:{relationship.type}]->(target)
{generate_set_property(relationship.nonidentifying_properties, strict_typing)}"""


def generate_merge_relationship_load_csv_clause(
    relationship: Relationship,
    source_node: Node,
    target_node: Node,
    csv_name: str,
    method: str = "api",
    batch_size: int = 10000,
    strict_typing: bool = True,
) -> str:
    """
    Generate a MERGE relationship clause for the LOAD CSV method.
    """

    command = ":auto " if method == "browser" else ""
    if source_node.label == target_node.label:
        return f"""{command}LOAD CSV WITH HEADERS FROM 'file:///{csv_name}' as row
CALL {{
    WITH row
    {generate_match_same_node_labels_clause(node=source_node)}
    MERGE (source)-[n:{relationship.type}]->(target)
    {generate_set_property(relationship.nonidentifying_properties, strict_typing)}
}} IN TRANSACTIONS OF {str(batch_size)} ROWS;
"""
    else:
        return f"""{command}LOAD CSV WITH HEADERS FROM 'file:///{csv_name}' as row
CALL {{
    WITH row
    {generate_match_node_clause(source_node).replace('(n:', '(source:')}
    {generate_match_node_clause(target_node).replace('(n:', '(target:')}
    MERGE (source)-[n:{relationship.type}]->(target)
    {generate_set_property(relationship.nonidentifying_properties, strict_typing)}
}} IN TRANSACTIONS OF {str(batch_size)} ROWS;
"""


def generate_node_key_constraint(label: str, unique_properties: List[Property]) -> str:
    """
    Generate a node key constraint.
    """
    props = "(" + ", ".join([f"n.{x.name}" for x in unique_properties]) + ")"
    return f"""CREATE CONSTRAINT {generate_constraints_key(label_or_type=label, unique_property=unique_properties)} IF NOT EXISTS FOR (n:{label}) REQUIRE {props} IS NODE KEY;\n"""


def generate_relationship_key_constraint(
    type: str, unique_properties: List[Property]
) -> str:
    """
    Generate a relationship key constraint.
    """
    props = "(" + ", ".join([f"r.{x.name}" for x in unique_properties]) + ")"
    return f"""CREATE CONSTRAINT {generate_constraints_key(label_or_type=type, unique_property=unique_properties)} IF NOT EXISTS FOR ()-[r:{type}]-() REQUIRE {props} IS RELATIONSHIP KEY;\n"""


def cast_value(prop: Property, strict_typing: bool = True) -> str:
    """
    format property to be cast to correct type during ingestion.
    """

    # take the first val as this is the identifying column
    csv_mapping = (
        prop.csv_mapping[0] if isinstance(prop.csv_mapping, list) else prop.csv_mapping
    )

    # escape bad chars
    csv_mapping = (
        f"`{csv_mapping}`"
        if not csv_mapping[0].isalnum() or " " in csv_mapping
        else csv_mapping
    )

    base = f"row.{csv_mapping}"

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


def format_pyingest_post_ingest_code(data: Union[str, List[str], None]) -> str:
    """
    Format the given post ingest code into a String to be injected into the
    PyIngest yaml file.
    """

    if isinstance(data, str) and ".cypher" not in data and ".cql" not in data:
        res = ""
        for cql in data.split(";")[:-1]:
            cql_formatted = cql.lstrip().replace("\n", "\n    ")
            res += f"  - {cql_formatted}\n"
        return res
    elif isinstance(data, str) and (".cypher" in data or ".cql" in data):
        with open(data, "r") as f:
            cql_file = f.read()
        res = ""
        for cql in cql_file.split(";")[:-1]:
            cql_formatted = cql.lstrip().replace("\n", "\n    ")
            res += f"  - {cql_formatted}\n"
        return res

    elif isinstance(data, list):
        res = ""
        for cql in data:
            cql_formatted = cql.lstrip().replace("\n", "\n    ")
            res += f"  - {cql_formatted}\n"
        return res
    else:
        raise ValueError(f"Unable to parse post ingest code. data: {data}")
