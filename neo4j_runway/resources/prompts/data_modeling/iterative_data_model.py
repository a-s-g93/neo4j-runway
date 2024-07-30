from typing import Optional
from .constants import DATA_MODEL_GENERATION_RULES, DATA_MODEL_GENERATION_RULES_ADVANCED
from ....inputs import UserInput
from .formatters import (
    format_column_descriptions,
    format_discovery_text,
    format_use_cases,
    format_user_corrections,
    format_general_description,
)


def create_data_model_iteration_prompt(
    discovery_text: str,
    user_input: UserInput,
    data_model_to_modify: "DataModel",  # type: ignore
    user_corrections: Optional[str] = None,
    use_yaml_data_model: bool = False,
) -> str:
    """
    Generate the prompt to iterate on the previous data model.
    """
    discovery = format_discovery_text(discovery_text)
    feature_descriptions = format_column_descriptions(user_input=user_input)
    use_cases = format_use_cases(user_input=user_input)
    user_corrections = format_user_corrections(user_corrections=user_corrections)
    general_description = format_general_description(user_input=user_input)

    prompt = f"""{general_description}
{discovery}
{feature_descriptions}
Based on your experience building high-quality graph data
models, please improve this graph data model according to the feedback below.

{user_corrections}
{data_model_to_modify.to_yaml(write_file=False) if use_yaml_data_model else data_model_to_modify}

{use_cases}
{DATA_MODEL_GENERATION_RULES}
{DATA_MODEL_GENERATION_RULES_ADVANCED}
"""

    return prompt
