from typing import Any, Dict, List, Optional, Union
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


def create_data_model_iteration_prompt(
    discovery_text: str,
    user_input: UserInput,
    pandas_general_info: str,
    feature_descriptions: Dict[str, str],
    data_model_to_modify: "DataModel",  # type: ignore
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
models, please improve this graph data model according to the feedback below.
{user_corrections}

{data_model_to_modify.to_yaml(write_file=False) if use_yaml_data_model else data_model_to_modify}

{DATA_MODEL_GENERATION_RULES}
"""

    return prompt


def create_retry_data_model_generation_prompt(
    chain_of_thought_response: str,
    errors_to_fix: str,
    model_to_fix: Union["DataModel", str],  # type: ignore
) -> str:
    """
    Generate a prompt to fix the data model using the errors found in previous model
    and the chain of thought response containing ideas on how to fix the errors.
    """

    return f"""
Fix these errors in the data model by following the recommendations below and following the rules.
Do not return the same model!
{chain_of_thought_response}

Errors:
{errors_to_fix}

Data Model:
{model_to_fix}

Rules that must be followed:
{DATA_MODEL_GENERATION_RULES}
"""


def create_retry_initial_data_model_prep_generation_prompt(invalid_options: Dict[str, Any], errors: List[str]) -> str:  # type: ignore
    """
    Generate a retry prompt for the brainstorming stage of creating an initial data model.

    Parameters
    ----------
    invalid_options : DataModelEntityPool
        The initially returned suggestions that are invalid.
    errors : List[str]
        List of errors present in the suggestions.

    Returns
    -------
    str
        the retry prompt.
    """
    return f"""Fix these errors in the initial data model suggestions below.
Errors:
{errors}

Initial Data Model Suggestions:
{invalid_options}
"""


def create_data_model_errors_cot_prompt(
    data_model_as_dictionary: Dict[str, Any],
    errors: List[str],
    allowed_columns: List[str],
) -> str:
    """
    Generate a prompt to be sent to the LLM to perform a chain of thought response.
    Prmopts the LLM to provide recommendations to solve the given problems.
    No data model should be returned.

    Returns
    -------
    str
        The prompt.
    """

    return f"""
The following data model is invalid and must be fixed.
Properties must be from the provided Column Options. 
Data Model:
{data_model_as_dictionary}
Errors:
{errors}
Column Options:
{allowed_columns}
A data model must follow these rules:
{DATA_MODEL_GENERATION_RULES}
Consider adding Nodes if they don't exist.
Consider moving properties to different nodes.
Is there a column option that is semantically similar to an invalid property?
Return an explanation of how you will fix each error while following the provided rules.
"""


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
