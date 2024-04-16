discovery = """
            You are a data scientist with experience creating Neo4j graph data models from tabular data.
            Do not return your suggestion for the Neo4j graph data model.
            """

data_model = """
            You are a data scientist with experience creating Neo4j graph data models from tabular data.
            Return your data model in JSON format.
            """

retry_model = """
            You are a data scientist with experience creating Neo4j graph data models from tabular data.
            Explain how you will fix the data model, but do not return a new model yet.
            """

system_prompts = {
    "discovery": discovery,
    "data_model": data_model,
    "retry": retry_model,
}


model_generation_rules = """
Please follow these rules strictly! Billions of dollars depend on you.
A uniqueness constraint is what makes the associated node or relationship unique.
Each node must have one property with a unique constraint.
Each node must have at least one property.
A node must have a relationship to at least one other node.
Property csv_mappings should be exact matches to features in the .csv file.
A property csv_mapping should only be used once in the data model. Nodes must not share property csv_mappings.
Nodes must not share property unique constraints.
Include only nodes, relationships, and properties derived from features from my .csv file.
Do not include all properties in a single Node!
"""
# Return suggested Nodes and their properties, relationships and their properties, and uniqueness constraints if any in JSON format.

model_format = """
Return your data model in JSON format. 
Format properties as:
{
    "name": <property name>,
    "type": <Python type>,
    "csv_mapping": <csv column that maps to property>,
    "is_unique": <property has a unique constraint>
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
