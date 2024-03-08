discovery = """
            You are a data scientist with experience creating Neo4j graph data models from tabular data.
            Do not return your suggestion for the Neo4j graph data model.
            """

data_model = """
            You are a data scientist with experience creating Neo4j graph data models from tabular data.
            Return your data model in JSON format.
            """

system_prompts = {
    "discovery": discovery,
    "data_model": data_model
}

data_model_format = """
Return your data model in JSON format. 
Format nodes as:
{{
    "label": <node label>,
    "properties": <list of node properties>,
    "unique_constraints": <list of properties with uniqueness constraints>,
}}
Format relationships as:
{{
    "type": <relationship type>,
    "properties": <list of relationship properties>,
    "unique_constraints": <list of properties with uniqueness constraints>,
    "source": <the node this relationship begins>,
    "target": <the node this relationship ends>,
    }}
Format your JSON as:
{{
"Nodes": {{nodes}},
"Relationships"{{relationships}}
}}
            """

model_generation_rules = """
Please return an updated graph data model with your suggested improvements in JSON format.
A uniqueness constraint is what makes the associated node or relationship unique.
Each node will have at least one unique constraint.
Each node must have at least one property that acts as a unique identifier.
If no properties or unique constraints are suggested return an empty list.
Properties should be exact matches to features in the .csv file.
Each feature in the .csv file should be used no more than one time!
Limit each node to at most five properties!
Do not return the same model!
"""

