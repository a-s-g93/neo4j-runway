from typing import Any, Dict, Optional

from .formatters import (
    get_rules,
)
from .template import create_data_modeling_prompt


def create_data_model_iteration_prompt(
    discovery_text: str,
    valid_columns: Dict[str, Any],
    data_model_to_modify: "DataModel",  # type: ignore
    multifile: bool,
    corrections: Optional[str] = None,
    data_dictionary: Optional[Dict[str, Any]] = None,
    use_cases: Optional[str] = None,
    use_yaml_data_model: bool = False,
    advanced_rules: bool = True,
) -> str:
    """
    Generate the prompt to iterate on the previous data model.
    """

    prefix = (
        "Please make corrections to the graph data model using the context provided."
    )
    rules = get_rules(multifile=multifile, advanced_rules=advanced_rules)

    return create_data_modeling_prompt(
        prefix=prefix,
        discovery=discovery_text,
        data_model=data_model_to_modify,
        data_model_as_yaml=use_yaml_data_model,
        corrections=corrections,
        data_dictionary=data_dictionary,
        use_cases=use_cases,
        rules=rules,
        multifile=multifile,
        valid_columns=valid_columns,
    )
