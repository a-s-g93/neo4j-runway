from functools import reduce
from typing import Any, Dict, List, Optional

# from ....models.core import DataModel
# from ...llm_response_types.initial_model_pool import DataModelEntityPool
from .constants import (
    DATA_MODEL_GENERATION_RULES_ADVANCED,
    DATA_MODEL_GENERATION_RULES_MULTI,
    DATA_MODEL_GENERATION_RULES_SINGLE,
)


def format_general_description(general_description: Optional[str]) -> str:
    if general_description is not None:
        return f"""Here is the data information:
{general_description}"""
    else:
        return ""


def format_discovery(text: Optional[str]) -> str:
    return (
        "Here are the initial discovery findings:\n" + f"{text}" + "\n\n"
        if text is not None
        else ""
    )


def format_data_dictionary(
    data_dictionary: Optional[Dict[str, Any]], multifile: bool
) -> str:
    assert data_dictionary is not None, "data dictionary must be provided."

    def _pretty_print() -> str:
        res = ""
        for file in data_dictionary.keys():
            res += f"{file}\n"
            for col, desc in data_dictionary[file].items():
                res += f"  * {col} : {desc}\n"
        return res

    if multifile:
        return (
            "The following is a description of each feature in the data and the file they belong to:\n"
            + f"{_pretty_print()}"
            + "\n\n"
        )
    else:
        return (
            "The following is a description of each feature in the data:\n"
            + f"{data_dictionary}"
            + "\n\n"
        )


def format_use_cases(use_cases: Optional[str]) -> str:
    return (
        "The final data model should address the following use cases:\n"
        + f"{use_cases}"
        + "\n\n"
        if use_cases is not None
        else ""
    )


def format_valid_columns(valid_columns: Dict[str, Any]) -> str:
    return f"""Properties must only be derived from these values:
{valid_columns}\n\n"""


def format_errors(errors: Optional[List[str]]) -> str:
    if errors is not None:
        pretty_errors = reduce(lambda a, b: a + b, ["* " + e + "\n" for e in errors])

        return f"""Errors:
{pretty_errors}\n\n"""
    else:
        return ""


def format_corrections(corrections: Optional[str]) -> str:
    if corrections is not None:
        return (
            """Based on your experience building high-quality graph data
models, please improve this graph data model. Focus on this feedback: \n"""
            + corrections
            + "\n\n"
        )
    else:
        return """Based on your experience building high-quality graph data
models, please improve this graph data model. Add features from the data to each node and relationship as properties.
Ensure that these properties provide value to their respective node or relationship.\n\n
"""


def format_data_model(data_model: "DataModel", yaml_format: bool = False) -> str:  # type: ignore
    return "Data Model:\n" + (
        str(data_model.to_yaml(write_file=False)) + "\n\n"
        if yaml_format
        else str(data_model.model_dump_json()) + "\n\n"
    )


def format_entity_pool(
    entity_pool: "DataModelEntityPool",  # type: ignore
    retry_prompt: bool = False,
) -> str:
    if not retry_prompt:
        return f"""Here are recommendations to base your graph data model on. Add necessary entities.
    {entity_pool.model_dump_json()}\n\n"""
    else:
        return f"""Here are the current entity suggestions:
    {entity_pool.model_dump_json()}\n\n"""


def get_rules(multifile: bool, advanced_rules: bool) -> str:
    base = "Rules that must be followed:\n" + (
        DATA_MODEL_GENERATION_RULES_MULTI
        if multifile
        else DATA_MODEL_GENERATION_RULES_SINGLE
    )

    if advanced_rules:
        base += "\n" + DATA_MODEL_GENERATION_RULES_ADVANCED

    return base
