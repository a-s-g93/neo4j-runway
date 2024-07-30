from typing import Dict, Optional

from ....inputs import UserInput


def format_general_description(user_input: UserInput) -> str:
    if user_input.general_description != "":
        return f"""Here is the csv data information:
{user_input.general_description}"""
    else:
        return ""


def format_discovery_text(text: Optional[str]) -> str:
    return (
        "Here is the initial discovery findings:\n" + f"{text}" + "\n\n"
        if text is not None
        else ""
    )


def format_column_descriptions(user_input: UserInput) -> str:
    return (
        "The following is a description of each feature in the data:\n"
        + f"{user_input.column_descriptions}"
        + "\n\n"
        if user_input.column_descriptions is not None
        else ""
    )


def format_use_cases(user_input: UserInput) -> str:

    return (
        "The final data model should address the following use cases:\n"
        + f"{user_input.pretty_use_cases}"
        + "\n\n"
        if user_input.use_cases is not None
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
