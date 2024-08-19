from typing import Any, Dict, Optional

from .constants import DATA_MODEL_GENERATION_RULES, DATA_MODEL_GENERATION_RULES_ADVANCED
from .formatters import (
    format_data_dictionary,
    format_discovery_text,
    format_general_description,
    format_use_cases,
    format_user_corrections,
)


def create_data_model_iteration_prompt(
    discovery_text: str,
    data_model_to_modify: "DataModel",  # type: ignore
    multifile: bool,
    user_corrections: Optional[str] = None,
    data_dictionary: Optional[Dict[str, Any]] = None,
    use_cases: Optional[str] = None,
    general_description: Optional[str] = None,
    use_yaml_data_model: bool = False,
    advanced_rules: bool = True,
) -> str:
    """
    Generate the prompt to iterate on the previous data model.
    """
    discovery = format_discovery_text(discovery_text)
    data_dictionary_text = format_data_dictionary(
        data_dictionary=data_dictionary,
        multifile=multifile,
    )
    use_cases = format_use_cases(use_cases=use_cases)
    general_description = format_general_description(
        general_description=general_description
    )
    user_corrections = format_user_corrections(user_corrections=user_corrections)

    prompt = f"""{general_description}
{discovery}
{data_dictionary_text}
Based on your experience building high-quality graph data
models, please improve this graph data model according to the feedback below.

{user_corrections}
{data_model_to_modify.to_yaml(write_file=False) if use_yaml_data_model else data_model_to_modify}

{use_cases}
{DATA_MODEL_GENERATION_RULES}
{DATA_MODEL_GENERATION_RULES_ADVANCED if advanced_rules else ""}
"""

    return prompt
