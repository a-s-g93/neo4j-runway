import os
from typing import Any, Dict, List, Optional, Set, Union

import pandas as pd

from ...exceptions import DataNotSupportedError
from .data_dictionary.column import Column
from .data_dictionary.data_dictionary import DataDictionary
from .data_dictionary.table_schema import TableSchema
from .data_dictionary.utils import load_data_dictionary_from_compact_python_dictionary
from .table import Table
from .table_collection import TableCollection


def load_local_files(
    data_directory: str,
    general_description: str = "",
    data_dictionary: Union[Dict[str, Any], DataDictionary] = dict(),
    use_cases: Optional[List[str]] = None,
    include_files: List[str] = list(),
    ignored_files: List[str] = list(),
    config: Dict[str, Dict[str, Any]] = dict(),
) -> TableCollection:
    """
    A function to systematically load all files from a local directory. Currently supported file formats are: [csv, json, jsonl].

    Parameters
    ----------
    data_directory : str
        The directory containing all data.
    general_description : str
        A general description of the data, by default None
    data_dictionary : Union[Dict[str, Any], DataDictionary], optional
        Either
            1. a dictionary with file names as keys. Each key has a dictionary containing a description of each column in the file that is available for data modeling.
               Only columns identified here will be considered for inclusion in the data model.
            2. A `DataDictionary` object
            By default dict()
    use_cases : Optional[List[str]], optional
        Any use cases that the graph data model should address, by default None
    include_files: List[str], optional
        Any filres in the directory that should be included. Overwrites `ignored_files` arg. By default list()
    ignored_files : List[str], optional
        Any files in the directory that should be ignored. Will be overwritten if `include_files` arg is provided. By default list()
    config : Dict[str, Dict[str, Any]], optional
        A dictionary with file names as keys. Each key has a dictionary containing arguments to pass to the Pandas load_* function. By default dict()

    Returns
    -------
    TableCollection
        The container for all loaded data.

    Raises
    ------
    DataNotSupportedError
        If an attempt is made to load an unsupported file.
    """

    files_to_load: Set[str] = set()

    if not include_files:
        files_to_load = set(os.listdir(data_directory) or set()).difference(
            set(ignored_files)
        )
    else:
        files_to_load = set(include_files)

    loaded_files: List[Table] = list()

    _check_files(files=files_to_load)

    if isinstance(data_dictionary, dict):
        data_dictionary = load_data_dictionary_from_compact_python_dictionary(
            python_dictionary=data_dictionary,
            file_name=list(files_to_load)[0] if len(files_to_load) > 1 else "file",
        )

    assert isinstance(
        data_dictionary, DataDictionary
    ), "`data_dictionary` is not a `DataDictionary` object."

    for f in files_to_load:
        table_schema = data_dictionary.get_table_schema(f)
        # allowed_columns = (
        #     list(data_dictionary.get(f, dict()))
        #     if f in data_dictionary.keys()
        #     else None
        # )

        conf = config.get(f, dict())
        # file_data_dict: Dict[str, str] = data_dictionary.get(f, data_dictionary)
        if f.lower().endswith(".json") or f.lower().endswith(".jsonl"):
            loaded_files.append(
                load_json(
                    file_path=data_directory + f,
                    general_description=general_description,
                    table_schema=table_schema,
                    use_cases=use_cases,
                    allowed_columns=table_schema.column_names,
                    config=conf,
                )
            )
        elif f.lower().endswith(".csv"):
            loaded_files.append(
                load_csv(
                    file_path=data_directory + f,
                    general_description=general_description,
                    table_schema=table_schema,
                    use_cases=use_cases,
                    allowed_columns=table_schema.column_names,
                    config=conf,
                )
            )
        else:
            raise DataNotSupportedError(f"File {f} is not in a supported format.")

    return TableCollection(
        data_directory=data_directory,
        tables=loaded_files,
        general_description=general_description,
        data_dictionary=data_dictionary,
        use_cases=use_cases,
        discovery=None,
    )


def load_csv(
    file_path: str,
    general_description: str = "",
    table_schema: Optional[TableSchema] = None,
    use_cases: Optional[List[str]] = None,
    allowed_columns: Optional[List[str]] = None,
    config: Dict[str, Any] = dict(),
) -> Table:
    if config.get("usecols") is None:
        config["usecols"] = allowed_columns or (
            table_schema.column_names if table_schema is not None else list()
        )
    try:
        data: pd.DataFrame = pd.read_csv(file_path, **config)
    except ValueError as e:
        raise ValueError(
            (
                f"File {file_path} was given column(s) {config['usecols']}, but some do not exist in the data.",
                e,
            )
        )

    name: str = file_path.split("/")[-1] if "/" in file_path else file_path

    return Table(
        name=name,
        dataframe=data,
        file_path=file_path,
        general_description=general_description,
        table_schema=table_schema
        or TableSchema(
            name=name, columns=[Column(name=col_name) for col_name in config["usecols"]]
        ),
        use_cases=use_cases,
        discovery_content=None,
    )


def load_json(
    file_path: str,
    general_description: str = "",
    table_schema: Optional[TableSchema] = None,
    use_cases: Optional[List[str]] = None,
    allowed_columns: Optional[List[str]] = None,
    config: Dict[str, Any] = dict(),
) -> Table:
    cols = allowed_columns or (
        table_schema.column_names if table_schema is not None else list()
    )

    # json lines config
    config["lines"] = True if file_path.lower().endswith("l") else False

    try:
        data: pd.DataFrame = pd.read_json(file_path, **config)[cols]
    except KeyError as e:
        raise KeyError(
            (
                f"File {file_path} was given column(s) {cols}, but some do not exist in the data.",
                e,
            )
        )

    name: str = file_path.split("/")[-1] if "/" in file_path else file_path

    return Table(
        name=name,
        file_path=file_path,
        dataframe=data,
        general_description=general_description,
        table_schema=table_schema
        or TableSchema(
            name=name, columns=[Column(name=col_name) for col_name in config["usecols"]]
        ),
        use_cases=use_cases,
        discovery_content=None,
    )


def _check_files(files: Set[str]) -> bool:
    """
    Validate that all files in data directory are compatible. This should be ran before attempting to load directory.
    """
    valid_formats: List[str] = ["csv", "json", "jsonl"]
    bad_files: List[str] = [f for f in files if f.split(".")[-1] not in valid_formats]
    if len(bad_files) > 0:
        raise DataNotSupportedError(
            f"File(s) {bad_files} is / are not in a supported format."
        )
    else:
        return True
