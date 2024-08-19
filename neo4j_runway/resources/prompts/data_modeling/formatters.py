from typing import Any, Dict, Optional

from ....inputs import UserInput


def format_general_description(general_description: Optional[str]) -> str:
    if general_description is not None:
        return f"""Here is the data information:
{general_description}"""
    else:
        return ""


def format_discovery_text(text: Optional[str]) -> str:
    return (
        "Here is the initial discovery findings:\n" + f"{text}" + "\n\n"
        if text is not None
        else ""
    )


def format_data_dictionary(
    data_dictionary: Optional[Dict[str, Any]], multifile: bool
) -> str:
    assert data_dictionary is not None, "data dictionary must be provided."
    if multifile:
        return (
            "The following is a description of each feature in the data and the file they belong to:\n"
            + f"{data_dictionary}"
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


def format_user_corrections(user_corrections: Optional[str]) -> str:
    if user_corrections is not None:
        return (
            "Focus on this feedback when refactoring the model: \n"
            + user_corrections
            + "\n\n"
        )
    else:
        return """Add features from the data to each node and relationship as properties.
Ensure that these properties provide value to their respective node or relationship.
"""
