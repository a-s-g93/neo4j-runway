from ....inputs import UserInput
import pandas as pd


def create_discovery_prompt(
    pandas_general_description: str,
    pandas_numeric_feature_descriptions: pd.DataFrame,
    pandas_categorical_feature_descriptions: pd.DataFrame,
    user_input: UserInput,
) -> str:
    """
    Generate the initial discovery prompt for a single Pandas DataFrame.
    """

    feature_descriptions: str = ""
    for col in pandas_numeric_feature_descriptions.columns:
        feature_descriptions += f"""{col}: {user_input.column_descriptions[col] if col in user_input.column_descriptions else ""} \n It has the following distribution: {pandas_numeric_feature_descriptions[col]} \n\n"""

    for col in pandas_categorical_feature_descriptions.columns:
        feature_descriptions += f"""{col}: {user_input.column_descriptions[col] if col in user_input.column_descriptions else ""} \n It has the following distribution: {pandas_categorical_feature_descriptions[col]} \n\n"""

    use_cases = (
        "Focus on information that will help answer these use cases: "
        + user_input.pretty_use_cases
        if user_input.use_cases is not None
        else ""
    )

    prompt = f"""
I want you to perform a preliminary analysis on my data to help us understand
its characteristics before we brainstorm about the graph data model.

{user_input.general_description}

The following is a summary of the data features, data types, and missing values:
{pandas_general_description}

The following is a description of each feature in the data:
{feature_descriptions}

{use_cases}
Provide me with your preliminary analysis of this data. What are important
overall details about the data? What are the most important features?
"""

    return prompt
