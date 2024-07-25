from typing import Dict, Optional
from ...models import DataModel
from ...inputs import UserInput

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


def create_initial_data_model_prompt(
    discovery_text: str,
    user_input: UserInput,
    pandas_general_info: str,
    feature_descriptions: Dict[str, str],
) -> str:
    """
    Generate the initial data model request prompt.
    """

    prompt = f"""
Here is the csv data information:
{user_input.general_description}

The following is a summary of the data features, data types, and missing values:
{pandas_general_info}

The following is a description of each feature in the data:
{feature_descriptions}

Here is the initial discovery findings:
{discovery_text}

Based upon your knowledge of the data in my .csv and 
of high-quality Neo4j graph data models, I would like you to return your
suggestion for translating the data in my .csv into a Neo4j graph data model.

{DATA_MODEL_GENERATION_RULES}

{DATA_MODEL_FORMAT}
            """
    return prompt


def create_data_model_iteration_prompt(
    discovery_text: str,
    user_input: UserInput,
    pandas_general_info: str,
    feature_descriptions: Dict[str, str],
    data_model_to_modify: DataModel,
    user_corrections: Optional[str] = None,
    use_yaml_data_model: bool = False,
) -> str:
    """
    Generate the prompt to iterate on the previous data model.
    """

    if user_corrections is not None:
        user_corrections = (
            "Focus on this feedback when refactoring the model: \n" + user_corrections
        )
    else:
        user_corrections = """Add features from the csv to each node and relationship as properties. 
Ensure that these properties provide value to their respective node or relationship.
"""

    prompt = f"""
Here is the csv data information:
{user_input.general_description}

The following is a summary of the data features, data types, and missing values:
{pandas_general_info}

The following is a description of each feature in the data:
{feature_descriptions}

Here is the initial discovery findings:
{discovery_text}

Based on your experience building high-quality graph data
models, are there any improvements you would suggest to this model?
{data_model_to_modify.to_yaml(write_file=False) if use_yaml_data_model else data_model_to_modify}

{user_corrections}

{DATA_MODEL_GENERATION_RULES}
"""

    return prompt
