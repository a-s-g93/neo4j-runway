"""
The Discovery module that handles summarization and discovery generation via an LLM.
"""

import asyncio
import io
import warnings
from typing import Any, Dict, List, Optional, Union

import pandas as pd
from IPython.display import (
    Markdown,
    display,
)
from numpy import number

from ..exceptions import PandasDataSummariesNotGeneratedError
from ..llm.base import BaseDiscoveryLLM
from ..resources.prompts.discovery import (
    create_discovery_prompt_multi_file,
    create_discovery_prompt_single_file,
    create_discovery_summary_prompt,
)
from ..utils.data import (
    DataDictionary,
    Table,
    TableCollection,
    create_data_dictionary_from_pandas_dataframe,
)
from ..warnings import ExperimentalFeatureWarning
from .discovery_content import DiscoveryContent


class Discovery:
    """
    Handles discovery generation for the provided data via Pandas and LLM analysis.
    """

    def __init__(
        self,
        data: Union[pd.DataFrame, Table, TableCollection],
        llm: Optional[BaseDiscoveryLLM] = None,
        data_dictionary: Optional[DataDictionary] = None,
        general_description: Optional[str] = None,
        file_name: Optional[str] = None,
        use_cases: Optional[List[str]] = None,
    ) -> None:
        """
        Handles discovery generation for the provided data via Pandas and LLM analysis.

        Parameters
        ----------
        data : Union[pd.DataFrame, Table, TableCollection]
            The data to run discovery on. Can be either a Pandas DataFrame, Runway Table or Runway TableCollection.
            Multi file inputs should be provided via the TableCollection class.
            Single file inputs may be provided as a DataFrame or Runway Table. They will be placed in a TableCollection class upon initialization of the Discovery class.
        llm : Optional[BaseDiscoveryLLM], optional
            The LLM instance used to generate data discovery.
            If running discovery for multiple files,
            it is recommended to use an async compatible LLM and use the `run_async` method.
            Not required if only interested in generating Pandas summaries. By default None.
        data_dictionary : Optional[DataDictionary], optional
            A `DataDictionary` object describing the data, by default None
        general_description : Optional[str], optional
            A general description of the data, by default None
        file_name : Optional[str], optional
            The file name, if providing only a single file, by default None
        use_cases : Optional[List[str]], optional
            A list of use cases that should be addressed by the final graph data model, by default None

        Raises
        ------
        ValueError
            Invalid data is provided.
        """

        self.llm = llm

        # self.data must be a TableCollection
        # precedence
        #   1. Table / TableCollection content
        #   2. UserInput content
        if isinstance(data, pd.DataFrame):
            cols = (
                data_dictionary.table_schemas[0].column_names
                if data_dictionary is not None
                else None
            )
            data_dictionary = (
                create_data_dictionary_from_pandas_dataframe(
                    dataframe=data, name=file_name or "file"
                )
                if data_dictionary is None
                else data_dictionary
            )
            file_name = data_dictionary.table_schemas[0].name

            t = Table(
                name=file_name or "file",
                file_path="",
                dataframe=data[cols] if cols is not None else data,
                general_description=general_description or "",
                table_schema=data_dictionary.get_table_schema(file_name or "file"),
                use_cases=use_cases,
            )
            self.data = TableCollection(
                data_directory="",
                tables=[t],
                general_description=t.general_description,
                data_dictionary=data_dictionary,
                use_cases=t.use_cases,
            )
        elif isinstance(data, Table):
            data_dir = "".join(data.file_path.split("/")[:-1])
            self.data = TableCollection(
                data_directory=data_dir,
                tables=[data],
                general_description=data.general_description,
                data_dictionary=DataDictionary(table_schemas=[data.table_schema]),
                use_cases=data.use_cases,
            )
        elif isinstance(data, TableCollection):
            self.data = data
        else:
            raise ValueError(
                "Provided data is not of an accepted type. Must be Pandas DataFrame, Runway Table or Runway TableCollection."
            )

        self._discovery_ran = False

        if self.is_multifile:
            warnings.warn(
                message="Multi file Discovery is an experimental feature and may not work as expected. Please use with caution and raise any issues encountered here: https://github.com/a-s-g93/neo4j-runway/issues",
                category=ExperimentalFeatureWarning,
            )

    @property
    def data_dictionary(self) -> DataDictionary:
        """
        The data dictionary describing the data.

        Returns
        -------
        DataDictionary
        """
        return self.data.data_dictionary

    @property
    def is_multifile(self) -> bool:
        """
        Whether data is multi-file or not.

        Returns
        -------
        bool
            True if multi-file detected, else False
        """

        return self.data_dictionary.is_multifile

    @property
    def discovery(self) -> str:
        """
        The final generated discovery for the data.

        Returns
        -------
        str
            The `discovery` attribute of the `data` attribute.
        """

        assert self.data.discovery is not None, "No generated discovery information."

        return self.data.discovery

    def _generate_data_summaries(self, ignore_files: List[str] = list()) -> None:
        """
        Generate the data summaries for each Table in the TableCollection.
        """

        for i in range(0, self.data.size):
            if self.data.tables[i].name not in ignore_files:
                ref: Table = self.data.tables[i]
                buffer = io.StringIO()
                ref.dataframe.info(buf=buffer)

                df_info = buffer.getvalue()
                try:
                    desc_numeric = ref.dataframe.describe(
                        percentiles=[0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99],
                        include=[number],
                    )
                except ValueError as e:
                    desc_numeric = pd.DataFrame()
                try:
                    desc_categorical = ref.dataframe.describe(include="object")
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
        This method is compatible with non-async LLM classes. If using an async LLM, please use the `run_async` method instead.
        Access generated discovery with the .view_discovery() method of the Discovery class.

        If running multi-file discovery, the parameter priority is as follows:
        1. custom_batches
        2. bulk_process
        3. num_calls
        4. batch_size

        If more than one of the above is provided, the highest priority will overwrite any others.

        Parameters
        ----------
        show_result : bool, optional
            Whether to print the final generated discovery upon retrieval. By default True
        notebook : bool, optional
            Whether code is executed in a notebook. Affects the result print formatting. By default True
        ignore_files : List[str], optional
            A list of files to ignore. For multi-file input. By default list()
        batch_size : int, optional
            The number of files to include in a discovery call. For multi-file input. By default 1
        bulk_process : bool, optional
            Whether to include all files in a single batch. For multi-file input. By default False
        num_calls : Optional[int], optional
            The max number of LLM calls to make during the discovery process. For multi-file input. By default None
        custom_batches : Optional[List[List[str]]], optional
            A list of custom batches to run discovery on. For multi-file input. By default None
        pandas_only : bool, optional
            Whether to only run Pandas summary generation and skip LLM calls. By default False

        Raises
        ------
        RuntimeError
            If an async LLM is provided to the Discovery constructor.
        PandasDataSummariesNotGeneratedError
            If Pandas summaries are unable to be generated.
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
            for t in self.data.tables:
                if t.name not in ignore_files and t.discovery_content is not None:
                    t.discovery_content.discovery = t.discovery_content.pandas_response
        # single file input LLM call
        elif self.data.size == 1:
            if self.data.tables[0].discovery_content is not None:
                response = self.llm._get_discovery_response(
                    formatted_prompt=create_discovery_prompt_single_file(
                        user_provided_general_data_description=self.data.general_description
                        or "",
                        pandas_general_description=self.data.tables[
                            0
                        ].discovery_content.pandas_general_description,
                        pandas_categorical_feature_descriptions=self.data.tables[
                            0
                        ].discovery_content.pandas_categorical_description,
                        pandas_numeric_feature_descriptions=self.data.tables[
                            0
                        ].discovery_content.pandas_numerical_description,
                        table_schema=self.data.data_dictionary.table_schemas[0],
                        use_cases=self.data.pretty_use_cases,
                    )
                )

                self.data.discovery = response
                self.data.tables[0].discovery_content.discovery = response

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
        Run the discovery process on the provided data asynchronously.
        This method is compatible with async LLM classes. If using a non async LLM, please use the `run` method instead.
        Access generated discovery with the .view_discovery() method of the Discovery class.

        If running multi-file discovery, the parameter priority is as follows:
        1. custom_batches
        2. bulk_process
        3. num_calls
        4. batch_size

        If more than one of the above is provided, the highest priority will overwrite any others.

        Parameters
        ----------
        show_result : bool, optional
            Whether to print the final generated discovery upon retrieval. By default True
        notebook : bool, optional
            Whether code is executed in a notebook. Affects the result print formatting. By default True
        ignore_files : List[str], optional
            A list of files to ignore. For multi-file input. By default list()
        batch_size : int, optional
            The number of files to include in a discovery call. For multi-file input. By default 1
        bulk_process : bool, optional
            Whether to include all files in a single batch. For multi-file input. By default False
        num_calls : Optional[int], optional
            The max number of LLM calls to make during the discovery process. For multi-file input. By default None
        custom_batches : Optional[List[List[str]]], optional
            A list of custom batches to run discovery on. For multi-file input. By default None

        Raises
        ------
        RuntimeError
            If a non async LLM is provided to the Discovery constructor.
        """

        assert self.llm is not None

        if not self.llm.is_async:
            raise RuntimeError(
                "Provided LLM class does not contain an async client. Please provide a different LLM or use the 'run' method instead."
            )

        if notebook:
            try:
                import nest_asyncio

                nest_asyncio.apply()
            except ImportError as e:
                raise ImportError(
                    "Could not import nest_asyncio library."
                    "This is required to run async methods in a Python Notebook."
                    "Please install with `pip install nest_asyncio`."
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
            assert (
                self.llm is not None
            ), "No llm arg was provided to the Discovery constructor."

            # prompt ids are the index
            ordered_prompts: List[str] = [
                prompt_dicts["prompt_id_to_prompt"][x]
                for x in sorted(prompt_dicts["prompt_id_to_prompt"])
            ]

            tasks = [self.llm._get_async_discovery_response(p) for p in ordered_prompts]

            responses = await asyncio.gather(*tasks)

            return {
                str(idx): responses[idx].response for idx in range(len(ordered_prompts))
            }

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

    def to_txt(
        self, file_dir: str = "./", file_name: str = "all", include_pandas: bool = True
    ) -> None:
        """
        Output findings to a .txt file.

        Parameters
        ----------
        file_dir : str, optional
            The directory to save files to, by default "./"
        file_name : str, optional
            'all' to export all data, 'final' to export only final discovery result, file name to export the desired file only, by default "all"
        include_pandas : bool, optional
            Whether to include the Pandas summaries, by default True
        """

        self._export_to_files(
            file_type=".txt",
            file_dir=file_dir,
            file_name=file_name,
            include_pandas=include_pandas,
        )

    def to_markdown(
        self, file_dir: str = "./", file_name: str = "all", include_pandas: bool = True
    ) -> None:
        """
        Output findings to a .md file.

        Parameters
        ----------
        file_dir : str, optional
            The directory to save files to, by default "./"
        file_name : str, optional
            'all' to export all data, 'final' to export only final discovery result, file name to export the desired file only, by default "all"
        include_pandas : bool, optional
            Whether to include the Pandas summaries, by default True
        """

        self._export_to_files(
            file_type=".md",
            file_dir=file_dir,
            file_name=file_name,
            include_pandas=include_pandas,
        )

    def _export_to_files(
        self,
        file_type: str,
        file_dir: str = "./",
        file_name: str = "all",
        include_pandas: bool = True,
    ) -> None:
        assert file_type in [
            ".txt",
            ".md",
        ], f"Unsupported file type provided: {file_type}."

        if file_name == "final":
            self.data._export_to_file(
                file_dir=file_dir, file_name="final_discovery" + file_type
            )
        elif file_name == "all":
            self.data._export_to_file(
                file_dir=file_dir, file_name="final_discovery" + file_type
            )
            for t in self.data.tables:
                assert (
                    t.discovery_content is not None
                ), f"`discovery_content` for table {t.name} can not be None."

                if "." in t.name:
                    name = t.name.split(".")[0] + "_discovery" + file_type
                else:
                    name = t.name + "_discovery" + file_type
                t.discovery_content._export_to_file(
                    file_dir=file_dir,
                    file_name=name,
                    include_pandas=include_pandas,
                )
        elif file_name in self.data.table_dict:
            t = self.data.table_dict[file_name]

            assert (
                t.discovery_content is not None
            ), f"`discovery_content` for table {t.name} can not be None."

            if "." in t.name:
                name = t.name.split(".")[0] + "_discovery" + file_type
            else:
                name = t.name + "_discovery" + file_type
            t.discovery_content._export_to_file(
                file_dir=file_dir,
                file_name=name,
                include_pandas=include_pandas,
            )
        else:
            raise ValueError(
                f"Table with file_name {file_name} not found in TableCollection."
            )


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
        tables = [t for t in data.tables if t.name not in ignore_files]

        table_to_prompt_id.update({t.name: str(prompt_id) for t in tables})

        prompt_id_to_prompt[str(prompt_id)] = create_discovery_prompt_multi_file(
            user_provided_general_data_description=data.general_description,
            data=data.tables,
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
                    for t in data.tables[i : i + batch_size]
                    if t.name not in ignore_files
                ]
                table_to_prompt_id.update(
                    {
                        t.name: str(prompt_id)
                        for t in data.tables[i : i + batch_size]
                        if t.name not in ignore_files
                    }
                )

            else:
                tables = [t for t in data.tables[i:] if t.name not in ignore_files]
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
                    for t in data.tables[i : i + batch_size]
                    if t.name not in ignore_files
                ]
                table_to_prompt_id.update(
                    {
                        t.name: str(prompt_id)
                        for t in data.tables[i : i + batch_size]
                        if t.name not in ignore_files
                    }
                )
            else:
                tables = [
                    data.table_dict[t.name]
                    for t in data.tables[i:]
                    if t.name not in ignore_files
                ]
                table_to_prompt_id.update(
                    {
                        t.name: str(prompt_id)
                        for t in data.tables[i:]
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
