discovery = """
You are a data scientist with experience creating Neo4j graph data models from tabular data.
Do not return your suggestion for the Neo4j graph data model.
"""

initial_data_model = """
You are a data scientist with experience creating Neo4j graph data models from tabular data.
Return your suggestions for nodes, relationships and properties in JSON format.
"""

data_model = """
You are a data scientist with experience creating Neo4j graph data models from tabular data.
Return your data model in JSON format.
"""

retry_model = """
You are a data scientist with experience creating Neo4j graph data models from tabular data.
Explain how you will fix the data model, but do not return a new model yet.
"""

SYSTEM_PROMPTS = {
    "discovery": discovery,
    "initial_data_model": initial_data_model,
    "data_model": data_model,
    "retry": retry_model,
}
