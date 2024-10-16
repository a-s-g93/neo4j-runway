from typing import Any, Dict, Optional

from .constants import (
    DATA_MODEL_FORMAT,
    NODE_GENERATION_RULES,
    NODES_FORMAT,
)
from .formatters import get_rules
from .template import create_data_modeling_prompt


def create_initial_nodes_prompt(
    discovery_text: str,
    multifile: bool,
    use_cases: Optional[str],
    valid_columns: Dict[str, Any],
    data_dictionary: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Generate a prompt to find nodes and properties to include in a data model.

    Returns
    -------
    str
        The prompt.
    """
    prefix = "Please generate a list of Nodes that will be used to construct a graph data model. Each node should represent an entity found in the data."

    return create_data_modeling_prompt(
        prefix=prefix,
        discovery=discovery_text,
        multifile=multifile,
        use_cases=use_cases,
        valid_columns=valid_columns,
        data_dictionary=data_dictionary,
        rules=NODE_GENERATION_RULES,
        data_model_format=NODES_FORMAT,
    )


def create_initial_data_model_prompt(
    discovery_text: str,
    data_model_recommendations: "Nodes",  # type: ignore
    multifile: bool,
    valid_columns: Dict[str, Any],
    data_dictionary: Optional[Dict[str, Any]] = None,
    use_cases: Optional[str] = None,
    advanced_rules: bool = True,
) -> str:
    """
    Generate the initial data model request prompt.
    """

    prefix = "I would like you to generate a graph data model based on this provided information. Ensure that the recommened nodes are implemented in the final data model."
    rules = get_rules(multifile=multifile, advanced_rules=advanced_rules)

    return create_data_modeling_prompt(
        prefix=prefix,
        discovery=discovery_text,
        nodes=data_model_recommendations,
        valid_columns=valid_columns,
        data_dictionary=data_dictionary,
        use_cases=use_cases,
        rules=rules,
        data_model_format=DATA_MODEL_FORMAT,
        multifile=multifile,
    )
