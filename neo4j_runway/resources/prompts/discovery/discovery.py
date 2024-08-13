from typing import Dict, List, Optional

import pandas as pd

from ....utils.data import Table


def create_discovery_prompt_single_file(
    user_provided_general_data_description: str,
    pandas_general_description: str,
    pandas_numeric_feature_descriptions: pd.DataFrame,
    pandas_categorical_feature_descriptions: pd.DataFrame,
    data_dictionary: Dict[str, str] = dict(),
    use_cases: Optional[List[str]] = None,
) -> str:
    """
    Generate the initial discovery prompt for a single Pandas DataFrame.
    """

    feature_descriptions: str = ""
    for col in pandas_numeric_feature_descriptions.columns:
        feature_descriptions += f"""{col}: {data_dictionary.get(col, "")}\nIt has the following distribution: {pandas_numeric_feature_descriptions[col]}\n\n"""

    for col in pandas_categorical_feature_descriptions.columns:
        feature_descriptions += f"""{col}: {data_dictionary.get(col, "")}\nIt has the following distribution: {pandas_categorical_feature_descriptions[col]}\n\n"""

    use_cases_text = (
        "Focus on information that will help answer these use cases: " + str(use_cases)
        if use_cases is not None
        else ""
    )

    prompt = f"""
I want you to perform a preliminary analysis on my data to help us understand
its characteristics before we brainstorm about the graph data model.

{user_provided_general_data_description}

The following is a summary of the data features, data types, and missing values:
{pandas_general_description}

The following is a description of each feature in the data:
{feature_descriptions}

{use_cases_text}
Provide me with your preliminary analysis of this data. What are important
overall details about the data? What are the most important features?
"""

    return prompt


def create_discovery_prompt_multi_file(
    user_provided_general_data_description: str,
    data: List[Table],
    total_files: int,
    use_cases: Optional[List[str]] = None,
) -> str:
    """
    Generate the initial discovery prompt for many Pandas DataFrames.
    """
    general_desc = (
        "\nThis is a general description of the entire dataset:\n"
        + user_provided_general_data_description
        if user_provided_general_data_description != ""
        else ""
    )

    use_cases_text = (
        "\nFocus on information that will help answer these use cases: "
        + str(use_cases)
        if use_cases is not None
        else ""
    )

    prefix = f"""I want you to perform a preliminary analysis on my data to help us understand
its characteristics before we brainstorm about the graph data model. The data is split into multiple files.
The information here pertains to {len(data)} of {total_files} files.
{general_desc}

"""

    suffix = f"""{use_cases_text}
Provide me with your preliminary analysis of this data. What are the most important features?
"""
    file_info = ""

    for t in data:
        feature_descriptions: str = ""
        if t.discovery_content is not None:
            for col in t.discovery_content.pandas_numerical_description.columns:
                feature_descriptions += f"""{col}: {t.data_dictionary.get(col, "")}\nIt has the following distribution: {t.discovery_content.pandas_numerical_description[col]}\n\n"""

            for col in t.discovery_content.pandas_categorical_description.columns:
                feature_descriptions += f"""{col}: {t.data_dictionary.get(col, "")}\nIt has the following distribution: {t.discovery_content.pandas_categorical_description[col]}\n\n"""

            file_info += f"""### {t.name}
The following is a summary of the data:
{t.discovery_content.pandas_general_description}

The following is a description of each feature in the data:
{feature_descriptions}
"""

    return prefix + file_info + suffix
