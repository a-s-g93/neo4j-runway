from typing import Any, Dict, List, Optional
from .constants import DATA_MODEL_GENERATION_RULES, DATA_MODEL_FORMAT
from ....inputs import UserInput


def create_initial_data_model_cot_prompt(
    discovery_text: str,
    feature_descriptions: Optional[Dict[str, str]],
    allowed_features: List[str],
) -> str:
    """
    Generate a prompt to find nodes, relationships and properties to include in a data model.
    This is only for brainstorming, result of prompt should not be a DataModel.

    Returns
    -------
    str
        The prompt.
    """
    discovery = (
        "Here is the initial discovery findings:\n" + f"{discovery_text}" + "\n"
        if discovery_text is not None
        else ""
    )
    feature_descriptions = (
        "The following is a description of each feature in the data:\n"
        + f"{feature_descriptions}"
        + "\n"
        if feature_descriptions is not None
        else ""
    )

    prompt = f"""{discovery}
{feature_descriptions}
Based upon the above information and of high-quality graph data models, 
return the following:
* Nodes and their respective properties
* Relationships and their respective source Nodes and target Nodes
* Relationships and thier respective properties, if any

All properties must be found in this list: {allowed_features}
Do not return an actual data model!
"""

    return prompt


def create_initial_data_model_prompt(
    discovery_text: str,
    data_model_recommendations: Dict[str, Any],
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

Here are recommendations to follow:
{data_model_recommendations}

Based upon the above information and of high-quality Neo4j graph data models, 
I would like you to translate the data in my .csv into a Neo4j graph data model.

{DATA_MODEL_GENERATION_RULES}

{DATA_MODEL_FORMAT}
"""
    return prompt
