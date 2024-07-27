DATA_MODEL_GENERATION_RULES = """
Please follow these rules strictly! Billions of dollars depend on you.
A uniqueness constraint is what makes the associated node or relationship unique.
A node key is a unique combination of two properties that distinguishes a node.
Each node must have one property with a unique constraint or two properties that make a node key.
Each node must have at least one property.
A node must have a relationship to at least one other node.
Property csv_mappings should be exact matches to features in the .csv file.
A property csv_mapping should only be used once in the data model. Nodes must not share property csv_mappings.
Nodes must not share property unique constraints.
Include only nodes, relationships, and properties derived from features from my .csv file.
Do not include all properties in a single Node!
"""

DATA_MODEL_FORMAT = """
Return your data model in JSON format. 
Format properties as:
{
    "name": <property name>,
    "type": <Python type>,
    "csv_mapping": <csv column that maps to property>,
    "csv_mapping_other": <a second csv column that maps to property, identifies relationship between two nodes of the same label>,
    "is_unique": <property has a unique constraint>,
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
