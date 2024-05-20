import io
import os
from typing import Dict, Union

import pandas as pd

from ..llm.llm import LLM
from ..objects.user_input import UserInput


class Discovery:

    def __init__(
        self, llm: LLM, user_input: Union[Dict[str, str], UserInput], data: pd.DataFrame
    ) -> None:
        if isinstance(user_input, UserInput):
            self.user_input = user_input.formatted_dict
        else:
            self.user_input = user_input
            assert "general_description" in self.user_input.keys(), (
                "user_input must include key:value pair {general_description: ...}. "
                + f"Found keys {self.user_input.keys()}"
            )
        self.llm = llm

        self.columns_of_interest = list(self.user_input.keys())
        self.columns_of_interest.remove("general_description")

        self.data = data[self.columns_of_interest]

        self._discovery_ran = False
        self.discovery = ""

    def _generate_csv_summary(self) -> Dict[str, pd.DataFrame]:
        """
        Generate the data summaries.
        """
        buffer = io.StringIO()
        self.data.info(buf=buffer)

        df_info = buffer.getvalue()
        desc_numeric = self.data.describe(
            percentiles=[0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99]
        )
        desc_categorical = self.data.describe(include="object")

        self.df_info = df_info
        self.numeric_data_description = desc_numeric
        self.categorical_data_description = desc_categorical

    def _generate_discovery_prompt(self) -> str:
        """
        Generate the initial discovery prompt.
        """

        self.feature_descriptions = ""
        for col in self.numeric_data_description.columns:
            self.feature_descriptions += f"{col}: {self.user_input[col]} \n It has the following distribution: {self.numeric_data_description[col]} \n\n"

        for col in self.categorical_data_description.columns:
            self.feature_descriptions += f"{col}: {self.user_input[col]} \n It has the following distribution: {self.categorical_data_description[col]} \n\n"

        prompt = f"""
                I want you to perform a preliminary analysis on my data to help us understand
                its characteristics before we brainstorm about the graph data model.

                This is a general description of the data:
                {self.user_input['general_description']}

                The following is a summary of the data features, data types, and missing values:
                {self.df_info}

                The following is a description of each feature in the data:
                {self.feature_descriptions}

                Provide me with your preliminary analysis of this data. What are important
                overall details about the data? What are the most important features?
                """

        return prompt

    def run(self) -> str:
        """
        Run discovery on the data.
        """

        self._generate_csv_summary()

        response = self.llm.get_discovery_response(
            formatted_prompt=self._generate_discovery_prompt()
        )

        self._discovery_ran = True
        self.discovery = response

        return response

    def to_txt(self, file_dir: str = "./", file_name: str = "discovery") -> None:
        """
        Save the generated discovery to a .txt file.
        """

        if file_dir != "./":
            os.makedirs(file_dir, exist_ok=True)

        with open(f"./{file_dir}{file_name}.txt", "w") as f:

            f.write(
                f"""
Data General Info
{self.df_info}

Numeric Data Descriptions
{self.numeric_data_description}

Categorical Data Descriptions
{self.categorical_data_description}

LLM Generated Discovery
{self.discovery}
            """
            )

    def to_markdown(self, file_dir: str = "./", file_name: str = "discovery") -> None:
        """
        Save the generated discovery to a .md file.
        """

        if file_dir != "./":
            os.makedirs(file_dir, exist_ok=True)

        with open(f"./{file_dir}{file_name}.md", "w") as f:
            f.write(
                f"""
Data General Info
{self.df_info}

Numeric Data Descriptions
{self.numeric_data_description}

Categorical Data Descriptions
{self.categorical_data_description}

LLM Generated Discovery
{self.discovery}
            """
            )
