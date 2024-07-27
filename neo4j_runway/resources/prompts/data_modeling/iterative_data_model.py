from typing import Dict, Optional
from .constants import DATA_MODEL_GENERATION_RULES
from ....inputs import UserInput


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
