# DATA_MODEL_GENERATION_RULES = """
# Please follow these rules strictly! Billions of dollars depend on you.
# A uniqueness constraint is what makes the associated node or relationship unique.
# A node key is a unique combination of two properties that distinguishes a node.
# Each node must have one property with a unique constraint or two properties that make a node key.
# Each node must have at least one property.
# A node must have a relationship to at least one other node.
# Property csv_mappings should be exact matches to features in the .csv file.
# A property csv_mapping should only be used once in the data model. Nodes must not share property csv_mappings.
# Nodes must not share property unique constraints.
# Include only nodes, relationships, and properties derived from features from my .csv file.
# Do not include all properties in a single Node!
# """

DATA_MODEL_GENERATION_RULES = """
Please follow these rules strictly! Billions of dollars depend on you.
Nodes
* Each node must have a unique property or node key pair
* Each node must have a relationship with at least one other node
* Unique properties and node keys may NOT be shared between different nodes
Relationships
* Relationships do NOT require uniqueness or properties
* NEVER use symmetric relationships
* Do NOT create self-referential relationships
Properties
* A csv_mapping must be an exact match to features in the .csv file
* A csv_mapping may only be used ONCE in a data model. It may NOT be shared between nodes
* A property may NOT be unqiue AND a key
General
* Do NOT return a single-node data model
* If a cycle exists, consider removing a relationship while maintaining the meaning captured by the cycle
* Do NOT generate csv_name values on Properties
"""

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
    csv_mapping_other indicates a unique feature on a target node that the source node has a relationship with. 
    Both csv_mapping and csv_mapping_other refer to the same node property name in the graph.
"""

DATA_MODEL_FORMAT = """
Return your data model in JSON format. 
Format properties as:
{
    "name": <property name>,
    "type": <Python type>,
    "csv_mapping": <csv column that maps to property>,
    "csv_mapping_other": <a second csv column that maps to property, identifies relationship between two nodes of the same label>,
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
