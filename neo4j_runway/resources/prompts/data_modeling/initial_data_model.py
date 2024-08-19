from typing import Any, Dict, Optional

from .constants import (
    DATA_MODEL_FORMAT,
    DATA_MODEL_GENERATION_RULES,
    DATA_MODEL_GENERATION_RULES_ADVANCED,
)
from .formatters import (
    format_data_dictionary,
    format_discovery_text,
    format_general_description,
    format_use_cases,
)


def create_initial_data_model_cot_prompt(
    discovery_text: str,
    multifile: bool,
    use_cases: str,
    data_dictionary: Optional[Dict[str, Any]] = None,
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
    data_dictionary_text = format_data_dictionary(
        data_dictionary=data_dictionary, multifile=multifile
    )
    use_cases = format_use_cases(use_cases=use_cases)

    prompt = f"""{discovery}
{data_dictionary_text}
{use_cases}
Based upon the above information and of high-quality graph data models,
return the following:
* Nodes and their respective properties
* Relationships and their respective possible source Nodes and target Nodes
* Relationships and their respective properties, if any
* Explanations for each decision and how it will benefit the data model
* All possible relationships for nodes

Remember
* All properties must be found in the data dictionary above!
* A node may not have properties from multiple files!
* A relationship may not have properties from multiple files!
* Do not return an actual data model!
"""

    return prompt


def create_initial_data_model_prompt(
    discovery_text: str,
    data_model_recommendations: Dict[str, Any],
    multifile: bool,
    data_dictionary: Optional[Dict[str, Any]] = None,
    use_cases: Optional[str] = None,
    general_description: Optional[str] = None,
    advanced_rules: bool = True,
) -> str:
    """
    Generate the initial data model request prompt.
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

    prompt = f"""{general_description}
{discovery}
{data_dictionary_text}

Here are recommendations to base your graph data model on:
{data_model_recommendations}

Based upon the above information and of high-quality Neo4j graph data models,
I would like you to translate this information into a Neo4j graph data model.

{use_cases}
{DATA_MODEL_GENERATION_RULES}
{DATA_MODEL_GENERATION_RULES_ADVANCED if advanced_rules else ""}

{DATA_MODEL_FORMAT}
"""
    return prompt
