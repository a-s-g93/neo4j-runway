DATA_MODEL_GENERATION_RULES = """
Please follow these rules strictly! Billions of dollars depend on you.
Nodes
* Each node must have a unique property or node key pair
* Each node must have a relationship with at least one other node
* Unique properties and node keys may NOT be shared between different nodes
* A node must only have a single ID property
Relationships
* Relationships do NOT require uniqueness or properties
* NEVER use symmetric relationships
* Do NOT create self-referential relationships
Properties
* A column_mapping must be an exact match to features in the file(s)
* A column_mapping may only be used ONCE in a data model. It may NOT be shared between nodes
* A property can NOT be both unique and a key
General
* Do NOT return a single-node data model
* If a cycle exists, consider removing a relationship while maintaining the meaning captured by the cycle
"""

DATA_MODEL_GENERATION_RULES_SINGLE = (
    DATA_MODEL_GENERATION_RULES
    + "* Do NOT generate `source_name` values on Nodes and Relationships"
)
DATA_MODEL_GENERATION_RULES_MULTI = (
    DATA_MODEL_GENERATION_RULES
    + """* Generate source_name values on Nodes and Relationships
* Ensure all properties are contained within the identified source.
* `alias` must be indicated for unique properties and is used to identify foreign keys of other tables.
* Many nodes or relationships may exist in a single file.
* Do NOT include property aliases in the data model."""
)

DATA_MODEL_GENERATION_RULES_ADVANCED = """
These are advanced data modeling best practices.
* Duplication of properties:
    Instead of having a repeated property on every node, you can
    have all of those nodes connected to a shared node with that property. This can make
    data updates massively easier.
* Decoration properties:
    If a property can't be used to answer a question, it is usually a waste of storage
* Intermediate / Event nodes:
    If you must implement a hyperedge, consider an Event node that has relationships with the desired source and target.
    This allows different nodes to share the same context.
* Super nodes:
    Stay away from super nodes, if possible. super nodes can be identified by low-cardinality unique properties
* Same label node relationships:
    alias indicates a unique feature on a target node that the source node has a relationship with.
    Both column_mapping and alias refer to the same node property name in the graph.
"""

DATA_MODEL_FORMAT = """
Return your data model in JSON format.
Format properties as:
{
    "name": <property name>,
    "type": <Python type>,
    "column_mapping": <csv column that maps to property>,
    "alias": <a second column that maps to property. identifies relationship between two nodes of the same label or a relationship that spans across different files>,
    "is_unique": <property is a unique identifier>,
    "part_of_key": <property is part of a node or relationship key>
}
Format nodes as:
{
    "label": <node label>,
    "properties": [properties]
}
Format relationships as:
{
    "type": <relationship type>,
    "properties": [properties],
    "source": <the node this relationship begins>,
    "target": <the node this relationship ends>
}
Format your data model as:
{
    "Nodes": [nodes],
    "Relationships": [relationships]
}
"""

ENTITY_POOL_GENERATION_RULES = """Based upon the above information and of high-quality graph data models,
return the following:
* Any possible Nodes and their respective properties
* Any possible Relationships and their respective source Nodes and target Nodes
* Relationships and their respective properties, if any
* Explanations for each decision and how it will benefit the data model
* All possible relationships for nodes
* `source_name` for all nodes and relationships

Remember
* All properties must be found in the data dictionary above!
* A property may have an alias in another file as a foreign key.
* A node may not have properties from multiple files!
* A relationship may not have properties from multiple files!
* Find properties that may uniquely identify Nodes"""
