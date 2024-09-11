"""
This file contains the function to generate a data modeling prompt from a template.
This ensures that all possible inputs are always structured in the same format regardless of the prompt task.
"""

from typing import Any, Dict, List, Optional

# from ....models.core import DataModel
# from ...llm_response_types.initial_model_pool import DataModelEntityPool
from .formatters import (
    format_corrections,
    format_data_dictionary,
    format_data_model,
    format_discovery,
    format_entity_pool,
    format_errors,
    format_use_cases,
    format_valid_columns,
)


def create_data_modeling_prompt(
    prefix: str,
    valid_columns: Dict[str, Any],
    rules: str,
    multifile: bool,
    data_model_as_yaml: bool = False,
    discovery: Optional[str] = None,
    data_dictionary: Optional[Dict[str, Any]] = None,
    errors: Optional[List[str]] = None,
    corrections: Optional[str] = None,
    data_model: Optional["DataModel"] = None,  # type: ignore
    entity_pool: Optional["DataModelEntityPool"] = None,  # type: ignore
    use_cases: Optional[str] = None,
    data_model_format: Optional[str] = None,
    retry_prompt: bool = False,
    suffix: Optional[str] = None,
) -> str:
    res = prefix + " "
    if discovery is not None:
        res += format_discovery(discovery)
    if data_dictionary is not None:
        res += format_data_dictionary(
            data_dictionary=data_dictionary, multifile=multifile
        )
    res += format_valid_columns(valid_columns=valid_columns)
    if errors is not None:
        res += format_errors(errors=errors)
    if corrections is not None:
        res += format_corrections(corrections=corrections)
    if data_model is not None:
        res += format_data_model(data_model=data_model, yaml_format=data_model_as_yaml)
    if entity_pool is not None:
        res += format_entity_pool(entity_pool=entity_pool, retry_prompt=retry_prompt)
    if use_cases is not None:
        res += format_use_cases(use_cases=use_cases)
    res += rules
    if data_model_format is not None:
        res += "\n" + data_model_format
    if suffix is not None:
        res += "\n" + suffix

    return res
