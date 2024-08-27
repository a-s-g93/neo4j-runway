from typing import Any, Dict, Optional

from ...llm_response_types.initial_model_pool import DataModelEntityPool
from .constants import DATA_MODEL_FORMAT, ENTITY_POOL_GENERATION_RULES
from .formatters import get_rules
from .template import create_data_modeling_prompt


def create_initial_data_model_cot_prompt(
    discovery_text: str,
    multifile: bool,
    use_cases: Optional[str],
    valid_columns: Dict[str, Any],
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
    prefix = "Please generate a pool of entities that will be used to construct a graph data model."

    return create_data_modeling_prompt(
        prefix=prefix,
        discovery=discovery_text,
        multifile=multifile,
        use_cases=use_cases,
        valid_columns=valid_columns,
        data_dictionary=data_dictionary,
        rules=ENTITY_POOL_GENERATION_RULES,
    )


def create_initial_data_model_prompt(
    discovery_text: str,
    data_model_recommendations: DataModelEntityPool,
    multifile: bool,
    valid_columns: Dict[str, Any],
    data_dictionary: Optional[Dict[str, Any]] = None,
    use_cases: Optional[str] = None,
    advanced_rules: bool = True,
) -> str:
    """
    Generate the initial data model request prompt.
    """

    prefix = "I would like you to generate a graph data model based on this provided information."
    rules = get_rules(multifile=multifile, advanced_rules=advanced_rules)

    return create_data_modeling_prompt(
        prefix=prefix,
        discovery=discovery_text,
        entity_pool=data_model_recommendations,
        valid_columns=valid_columns,
        data_dictionary=data_dictionary,
        use_cases=use_cases,
        rules=rules,
        data_model_format=DATA_MODEL_FORMAT,
        multifile=multifile,
    )
