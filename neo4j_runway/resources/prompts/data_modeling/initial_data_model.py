from typing import Any, Dict, List
from .constants import (
    DATA_MODEL_GENERATION_RULES,
    DATA_MODEL_GENERATION_RULES_ADVANCED,
    DATA_MODEL_FORMAT,
)
from ....inputs import UserInput
from .formatters import (
    format_column_descriptions,
    format_discovery_text,
    format_use_cases,
    format_general_description,
)


def create_initial_data_model_cot_prompt(
    discovery_text: str, allowed_features: List[str], user_input: UserInput
) -> str:
    """
    Generate a prompt to find nodes, relationships and properties to include in a data model.
    This is only for brainstorming, result of prompt should not be a DataModel.

    Returns
    -------
    str
        The prompt.
    """
    discovery = format_discovery_text(discovery_text)
    feature_descriptions = format_column_descriptions(user_input=user_input)
    use_cases = format_use_cases(user_input=user_input)

    prompt = f"""{discovery}
{feature_descriptions}
{use_cases}
Based upon the above information and of high-quality graph data models, 
return the following:
* Nodes and their respective properties
* Relationships and their respective possible source Nodes and target Nodes
* Relationships and their respective properties, if any
* Explanations for each decision and how it will benefit the data model 
* All possible relationships for nodes

Remember 
* All properties must be found in this list: {allowed_features}
* Do not return an actual data model!
"""

    return prompt


def create_initial_data_model_prompt(
    discovery_text: str,
    data_model_recommendations: Dict[str, Any],
    user_input: UserInput,
) -> str:
    """
    Generate the initial data model request prompt.
    """

    discovery = format_discovery_text(discovery_text)
    feature_descriptions = format_column_descriptions(user_input=user_input)
    use_cases = format_use_cases(user_input=user_input)
    general_description = format_general_description(user_input=user_input)

    prompt = f"""{general_description}
{discovery}
{feature_descriptions}
Based upon the above information and of high-quality Neo4j graph data models, 
I would like you to translate the data in my .csv into a Neo4j graph data model.

{use_cases}
{DATA_MODEL_GENERATION_RULES}
{DATA_MODEL_GENERATION_RULES_ADVANCED}

{DATA_MODEL_FORMAT}
"""
    return prompt
