"""
The Discovery module that handles summarization and discovery generation via an LLM.
"""

import io
import os
from typing import Dict, Optional, Union
import warnings

from IPython.display import display, Markdown  # type: ignore # this works even though I get an import warning for IPython...
import pandas as pd

from ..llm import LLM
from ..inputs import UserInput, user_input_safe_construct
from ..resources.prompts.discovery import create_discovery_prompt


class Discovery:
    """
    The Discovery module that handles summarization and discovery generation via an LLM.
    """

    def __init__(
        self,
        data: pd.DataFrame,
        user_input: Union[Dict[str, str], UserInput] = dict(),
        llm: Optional[LLM] = None,
        pandas_only: bool = False,
    ) -> None:
        """
        The Discovery module that handles summarization and discovery generation via an LLM.

        Attributes
        ----------
        llm : LLM, optional
            The LLM instance used to generate data discovery. Only required if pandas_only = False.
        user_input : Union[Dict[str, str], UserInput]
            User provided descriptions of the data.
            If a dictionary, then should contain the keys "general_description" and all desired columns., by default = {}
        data : pd.DataFrame
            The data in Pandas DataFrame format.
        pandas_only : bool
            Whether to only generate discovery using Pandas. Will not call the LLM service.
        """

        # we convert all user_input to a UserInput object
        if not isinstance(user_input, UserInput):
            self.user_input = user_input_safe_construct(
                unsafe_user_input=user_input, allowed_columns=data.columns
            )
        else:
            self.user_input = user_input

        self.llm = llm

        self.columns_of_interest = self.user_input.allowed_columns

        self.data = data[self.columns_of_interest]

        self.pandas_only = not self.llm or pandas_only
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

    def run(self, show_result: bool = True, notebook: bool = True) -> None:
        """
        Run the discovery process on the provided DataFrame.
        Access generated discovery with the .view_discovery() method of the Discovery class.

        Parameters
        -------
        show_result : bool
            Whether to print the generated discovery upon retrieval.
        notebook : bool
            Whether code is executed in a notebook. Affects the result print formatting.

        Returns
        ----------
        None
        """

        self._generate_csv_summary()

        if not self.pandas_only:
            response = self.llm._get_discovery_response(
                formatted_prompt=create_discovery_prompt(
                    pandas_general_description=self.df_info,
                    pandas_categorical_feature_descriptions=self.categorical_data_description,
                    pandas_numeric_feature_descriptions=self.numeric_data_description,
                    user_input=self.user_input,
                )
            )
        else:
            response = f"""Here are Summary Statistics generated with the Pandas Python library
            
{self.df_info}

{self.categorical_data_description}

{self.numeric_data_description}
"""

        self._discovery_ran = True
        self.discovery = response

        if show_result:
            self.view_discovery(notebook=notebook)

    def view_discovery(self, notebook: bool = True) -> None:
        """
        Print the discovery information.

        Parameters
        ----------
        notebook : bool, optional
            Whether executing in a notebook, by default True

        Returns
        ----------
        None
        """

        print(self.discovery) if not notebook else display(Markdown(self.discovery))

    def to_txt(self, file_dir: str = "./", file_name: str = "discovery") -> None:
        """
        Write the generated discovery to a .txt file.

        Parameters
        ----------
        file_dir : str, optional
            The file directory to write to, by default "./"
        file_name : str, optional
            The name of the file, by default "discovery"
        """

        if not file_name.endswith(".txt"):
            file_name = file_name + ".txt"

        if file_dir != "./":
            os.makedirs(file_dir, exist_ok=True)

        with open(f"./{file_dir}{file_name}", "w") as f:

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
        Write the generated discovery to a Markdown file.

        Parameters
        ----------
        file_dir : str, optional
            The file directory to write to, by default "./"
        file_name : str, optional
            The name of the file, by default "discovery"
        """

        if not file_name.endswith(".md"):
            file_name = file_name + ".md"

        if file_dir != "./":
            os.makedirs(file_dir, exist_ok=True)

        with open(f"./{file_dir}{file_name}", "w") as f:
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
