"""
The Discovery module that handles summarization and discovery generation via an LLM.
"""

import asyncio
import io
from typing import Any, Awaitable, Callable, Coroutine, Dict, List, Optional, Union

import pandas as pd
from IPython.display import (
    Markdown,
    display,
)
from numpy import number

from ..exceptions import PandasDataSummariesNotGeneratedError
from ..inputs import UserInput, user_input_safe_construct
from ..llm.base import BaseDiscoveryLLM
from ..resources.prompts.discovery import (
    create_discovery_prompt_multi_file,
    create_discovery_prompt_single_file,
    create_discovery_summary_prompt,
)
from ..utils.data import Table, TableCollection
from .discovery_content import DiscoveryContent


class Discovery:
    """
    The Discovery module that handles summarization and discovery generation via Pandas and an optional LLM.

    Attributes
    ----------
    llm : BaseDiscoveryLLM, optional
        The LLM instance used to generate data discovery. If not provided, then can only generate data summaries using Pandas.
    user_input : Union[Dict[str, str], UserInput]
        User provided descriptions of the data.
        If a dictionary, then should contain the keys "general_description" and all desired columns.
    data : Union[pd.DataFrame, Table, TableCollection]
        The data.
    """

    def __init__(
        self,
        data: Union[pd.DataFrame, Table, TableCollection],
        user_input: Union[Dict[str, str], UserInput] = dict(),
        llm: Optional[BaseDiscoveryLLM] = None,
    ) -> None:
        """
        The Discovery module that handles summarization and discovery generation via Pandas and an optional LLM.

        Parameters
        ----------
        llm : LLM, optional
            The LLM instance used to generate data discovery. Only required if pandas_only = False.
        user_input : Union[Dict[str, str], UserInput]
            User provided descriptions of the data.
            If a dictionary, then should contain the keys "general_description" and all desired columns. By default = {}
        data : pd.DataFrame
            The data in Pandas DataFrame format.
        """

        # we convert all user_input to a UserInput object
        if not isinstance(user_input, UserInput) and isinstance(data, pd.DataFrame):
            self.user_input = user_input_safe_construct(
                unsafe_user_input=user_input, allowed_columns=data.columns
            )
        elif isinstance(user_input, UserInput):
            self.user_input = user_input

        self.llm = llm

        # self.data must be a TableCollection
        # precedence
        #   1. Table / TableCollection content
        #   2. UserInput content
        if isinstance(data, pd.DataFrame):
            t = Table(
                name="",
                file_path="",
                data=data[self.user_input.allowed_columns],
                general_description=self.user_input.general_description,
                data_dictionary=self.user_input.column_descriptions,
                use_cases=self.user_input.use_cases,
            )
            self.data = TableCollection(
                data_directory="",
                data=[t],
                general_description=t.general_description,
                data_dictionary=t.data_dictionary,
                use_cases=t.use_cases,
            )
        elif isinstance(data, Table):
            data_dir = "".join(data.file_path.split("/")[:-1])
            self.data = TableCollection(
                data_directory=data_dir,
                data=[data],
                general_description=data.general_description,
                data_dictionary=data.data_dictionary,
                use_cases=data.use_cases,
            )
        elif isinstance(data, TableCollection):
            self.data = data
        else:
            raise ValueError(
                "provided data is not of an accepted type. Must be Pandas DataFrame, Runway Table or Runway TableCollection."
            )

        self._discovery_ran = False

    def _generate_data_summaries(self, ignore_files: List[str] = list()) -> None:
        """
        Generate the data summaries for each Table in the TableCollection.
        """

        for i in range(0, self.data.size):
            if self.data.data[i].name not in ignore_files:
                ref: Table = self.data.data[i]
                buffer = io.StringIO()
                ref.data.info(buf=buffer)

                df_info = buffer.getvalue()
                try:
                    desc_numeric = ref.data.describe(
                        percentiles=[0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99],
                        include=[number],
                    )
                except ValueError as e:
                    desc_numeric = pd.DataFrame()
                try:
                    desc_categorical = ref.data.describe(include="object")
                except ValueError as e:
                    desc_categorical = pd.DataFrame()

                ref.discovery_content = DiscoveryContent(
                    pandas_categorical_description=desc_categorical,
                    pandas_general_description=df_info,
                    pandas_numerical_description=desc_numeric,
                )

    def run(
        self,
        show_result: bool = True,
        notebook: bool = True,
        ignore_files: List[str] = list(),
        batch_size: int = 1,
        bulk_process: bool = False,
        num_calls: Optional[int] = None,
        custom_batches: Optional[List[List[str]]] = None,
        pandas_only: bool = False,
    ) -> None:
        """
        Run the discovery process on the provided data.
        Access generated discovery with the .view_discovery() method of the Discovery class.

        Parameters
        ----------
        show_result : bool
            Whether to print the generated discovery upon retrieval.
        notebook : bool
            Whether code is executed in a notebook. Affects the result print formatting.
        """

        if self.llm is not None and self.llm.is_async:
            raise RuntimeError(
                "Provided LLM class contains an async client. Please provide a different LLM or use the 'run_async' method instead."
            )

        self._generate_data_summaries(ignore_files=ignore_files)

        # single or multi Pandas only response
        if pandas_only or self.llm is None:
            response = self.data.get_pandas_summary(ignore_files=ignore_files)

            self.data.discovery = response
            for t in self.data.data:
                if t.name not in ignore_files and t.discovery_content is not None:
                    t.discovery_content.discovery = t.discovery_content.pandas_response
        # single file input LLM call
        elif self.data.size == 1:
            if self.data.data[0].discovery_content is not None:
                response = self.llm._get_discovery_response(
                    formatted_prompt=create_discovery_prompt_single_file(
                        user_provided_general_data_description=self.data.general_description
                        or "",
                        pandas_general_description=self.data.data[
                            0
                        ].discovery_content.pandas_general_description,
                        pandas_categorical_feature_descriptions=self.data.data[
                            0
                        ].discovery_content.pandas_categorical_description,
                        pandas_numeric_feature_descriptions=self.data.data[
                            0
                        ].discovery_content.pandas_numerical_description,
                        data_dictionary=self.data.data_dictionary,
                    )
                )

                self.data.discovery = response
                self.data.data[0].discovery_content.discovery = response

            else:
                raise PandasDataSummariesNotGeneratedError(
                    "Pandas data summaries were not generated somehow."
                )

        # multi file input LLM call
        else:
            # prompt_dicts contains table_to_prompt_id and prompt_id_to_prompt
            prompt_dicts: Dict[str, Any] = _create_discovery_prompts_for_multi_file(
                data=self.data,
                batch_size=batch_size,
                bulk_process=bulk_process,
                num_calls=num_calls,
                custom_batches=custom_batches,
                ignore_files=ignore_files,
            )

            prompt_id_to_response = {
                id: self.llm._get_discovery_response(p)
                for id, p in prompt_dicts["prompt_id_to_prompt"].items()
            }

            for name in prompt_dicts["table_to_prompt_id"].keys():
                response = prompt_id_to_response[
                    prompt_dicts["table_to_prompt_id"][name]
                ]
                if self.data.table_dict[name].discovery_content is not None:
                    self.data.table_dict[name].discovery = response

            # final summarization call
            self.data.discovery = self.llm._get_discovery_response(
                formatted_prompt=create_discovery_summary_prompt(
                    sub_discoveries=self.data.sub_discoveries,
                    use_cases=self.data.pretty_use_cases,
                )
            )

        self._discovery_ran = True

        if show_result:
            self.view_discovery(notebook=notebook)

    def run_async(
        self,
        show_result: bool = True,
        notebook: bool = True,
        ignore_files: List[str] = list(),
        batch_size: int = 1,
        bulk_process: bool = False,
        num_calls: Optional[int] = None,
        custom_batches: Optional[List[List[str]]] = None,
    ) -> None:
        """
        Run the discovery process on the provided data asynchronously. This method is only for multi-file inputs that require LLM calls.
        Use a non-async LLM class and the `run` method for single file inputs.
        Use the `run` method for Pandas only discovery.
        Access generated discovery with the .view_discovery() method of the Discovery class.

        Parameters
        ----------
        show_result : bool
            Whether to print the generated discovery upon retrieval.
        notebook : bool
            Whether code is executed in a notebook. Affects the result print formatting.
        """

        assert self.llm is not None

        if not self.llm.is_async:
            raise RuntimeError(
                "Provided LLM class does not contain an async client. Please provide a different LLM or use the 'run' method instead."
            )

        self._generate_data_summaries(ignore_files=ignore_files)

        # prompt_dicts contains table_to_prompt_id and prompt_id_to_prompt
        prompt_dicts: Dict[str, Any] = _create_discovery_prompts_for_multi_file(
            data=self.data,
            batch_size=batch_size,
            bulk_process=bulk_process,
            num_calls=num_calls,
            custom_batches=custom_batches,
            ignore_files=ignore_files,
        )

        async def _get_responses() -> Dict[str, str]:
            if self.llm is not None:
                # prompt ids are the index
                ordered_prompts: List[str] = [
                    prompt_dicts["prompt_id_to_prompt"][x]
                    for x in sorted(prompt_dicts["prompt_id_to_prompt"])
                ]

                tasks = [
                    self.llm._get_async_discovery_response(p) for p in ordered_prompts
                ]

                responses = await asyncio.gather(*tasks)
                return {
                    str(idx): responses[idx].response
                    for idx in range(len(ordered_prompts))
                }
            else:
                raise ValueError("No llm argument was provided.")

        def _run_async(method: Any) -> Any:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(method)

        prompt_id_to_response = _run_async(method=_get_responses())

        for name in prompt_dicts["table_to_prompt_id"].keys():
            assert self.data.table_dict[name].discovery_content is not None

            response = prompt_id_to_response[prompt_dicts["table_to_prompt_id"][name]]
            self.data.table_dict[name].discovery = response

        async def _get_summary_response() -> str:
            assert self.llm is not None

            tasks = [
                self.llm._get_async_discovery_response(
                    formatted_prompt=create_discovery_summary_prompt(
                        sub_discoveries=self.data.sub_discoveries,
                        use_cases=self.data.pretty_use_cases,
                    )
                )
            ]

            responses = await asyncio.gather(*tasks)
            return str(responses[0].response)

        # final summarization call
        self.data.discovery = _run_async(method=_get_summary_response())

        self._discovery_ran = True

        if show_result:
            self.view_discovery(notebook=notebook)

    def view_discovery(
        self, file_name: Optional[str] = None, notebook: bool = True
    ) -> None:
        """
        Print the discovery information of the provided file.
        If no file_name is provided, then displays the summarized final discovery.

        Parameters
        ----------
        file_name : str, optional
            The file to display discovery. If not provided, then displays the summarized final discovery. By default = None
        notebook : bool, optional
            Whether executing in a notebook, by default True
        """
        if file_name is None:
            discovery = self.data.discovery
        else:
            table = self.data.table_dict.get(file_name)
            if table is not None and table.discovery_content is not None:
                discovery = table.discovery
            else:
                raise ValueError(f"file_name {file_name} not found in data.")

        print(discovery) if not notebook else display(Markdown(discovery))

    def to_txt(self) -> str:
        return ""

    def to_markdown(self) -> str:
        return ""


def _create_discovery_prompts_for_multi_file(
    data: TableCollection,
    batch_size: int = 1,
    bulk_process: bool = False,
    num_calls: Optional[int] = None,
    custom_batches: Optional[List[List[str]]] = None,
    ignore_files: List[str] = list(),
) -> Dict[str, Any]:
    """
    Create prompts to feed to the DiscoveryLLM according to desired parameters.
    Priority of provided parameters is as follows:
    1. custom_batches
    2. bulk_process
    3. num_calls
    4. batch_size


    Parameters
    ----------
    batch_size : int, optional
        The number of files to include in a single prompt, by default 1
    bulk_process : bool, optional
        Whether to process all files at once in a single prompt, by default False
    num_calls : Optional[int], optional
        The number of LLM calls to make, by default None
    custom_batches : Optional[List[List[str]]], optional
        A list of desired file batches for processing, by default None
    ignore_files : List[str], optional
        Any files that should be ignored during discovery, by default list()

    Returns
    -------
    Dict[str, Any]
        A nested dictionary containing table_to_prompt_id and prompt_id_to_prompt.
    """
    # prompts: List[str] = list()
    table_to_prompt_id: Dict[str, str] = dict()
    prompt_id_to_prompt: Dict[str, str] = dict()
    prompt_id: int = 0

    if custom_batches is not None:
        # generate prompts containing each named file in batch

        for batch in custom_batches:
            tables = [data.table_dict[name] for name in batch]

            table_to_prompt_id.update({name: str(prompt_id) for name in batch})

            prompt_id_to_prompt[str(prompt_id)] = create_discovery_prompt_multi_file(
                user_provided_general_data_description=data.general_description,
                data=tables,
                use_cases=data.pretty_use_cases,
                total_files=data.size,
            )
            prompt_id += 1

    elif bulk_process:
        # call discovery with single prompt
        tables = [t for t in data.data if t.name not in ignore_files]

        table_to_prompt_id.update({t.name: str(prompt_id) for t in tables})

        prompt_id_to_prompt[str(prompt_id)] = create_discovery_prompt_multi_file(
            user_provided_general_data_description=data.general_description,
            data=data.data,
            use_cases=data.pretty_use_cases,
            total_files=data.size,
        )

    elif num_calls is not None:
        num_calls -= 1  # there is always a summarization call
        if num_calls < 1:
            num_calls = 1
        # split files into equal sizes according to desired number of LLM calls
        batch_size = data.size // num_calls + 1

        for i in range(0, data.size, batch_size):
            if i + batch_size < data.size:
                tables = [
                    t
                    for t in data.data[i : i + batch_size]
                    if t.name not in ignore_files
                ]
                table_to_prompt_id.update(
                    {
                        t.name: str(prompt_id)
                        for t in data.data[i : i + batch_size]
                        if t.name not in ignore_files
                    }
                )

            else:
                tables = [t for t in data.data[i:] if t.name not in ignore_files]
                table_to_prompt_id.update({t.name: str(prompt_id) for t in tables})

            prompt_id_to_prompt[str(prompt_id)] = create_discovery_prompt_multi_file(
                user_provided_general_data_description=data.general_description,
                data=tables,
                use_cases=data.pretty_use_cases,
                total_files=data.size,
            )

            prompt_id += 1

    else:
        # create n prompts where each prompt contains m files
        for i in range(0, data.size, batch_size):
            if i + batch_size < data.size:
                tables = [
                    data.table_dict[t.name]
                    for t in data.data[i : i + batch_size]
                    if t.name not in ignore_files
                ]
                table_to_prompt_id.update(
                    {
                        t.name: str(prompt_id)
                        for t in data.data[i : i + batch_size]
                        if t.name not in ignore_files
                    }
                )
            else:
                tables = [
                    data.table_dict[t.name]
                    for t in data.data[i:]
                    if t.name not in ignore_files
                ]
                table_to_prompt_id.update(
                    {
                        t.name: str(prompt_id)
                        for t in data.data[i:]
                        if t.name not in ignore_files
                    }
                )

            prompt_id_to_prompt[str(prompt_id)] = create_discovery_prompt_multi_file(
                user_provided_general_data_description=data.general_description,
                data=tables,
                use_cases=data.pretty_use_cases,
                total_files=data.size,
            )

            prompt_id += 1

    return {
        "table_to_prompt_id": table_to_prompt_id,
        "prompt_id_to_prompt": prompt_id_to_prompt,
    }
