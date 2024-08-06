import os
from typing import Any, Dict, List, Optional, Set
import warnings

import pandas as pd

from .table import Table, TableCollection
from ...exceptions import DataNotSupportedError


def load_local_files(
    data_directory: str,
    general_description: Optional[str] = None,
    data_dictionary: Optional[Dict[str, Dict[str, str]]] = None,
    use_cases: Optional[List[str]] = None,
    ignored_files: Optional[List[str]] = None,
    config: Optional[Dict[str, Dict[str, Any]]] = None,
) -> TableCollection:
    
    ignored_files: Set[str] = set(ignored_files) if ignored_files is not None else set()
    files_to_load: Set[str] = set(os.listdir(data_directory)).difference(ignored_files)
    loaded_files: List[Table] = list()

    _check_files(files=files_to_load)

    for f in files_to_load:
        allowed_columns = data_dictionary.get(f)
        conf = config.get(f)
        if f.lower().endswith(".json"):
            loaded_files.append(
                load_json(
                    file_path=data_directory + f,
                    general_description=general_description,
                    data_dictionary=data_dictionary[f],
                    use_cases=use_cases,
                    allowed_columns=list(allowed_columns.keys()) if allowed_columns else None,
                    config=conf,
                )
            )
        elif f.lower().endswith(".csv"):
            loaded_files.append(
                load_csv(
                    file_path=data_directory + f,
                    general_description=general_description,
                    data_dictionary=data_dictionary[f],
                    use_cases=use_cases,
                    allowed_columns=list(allowed_columns.keys()) if allowed_columns else None,
                    config=conf,
                )
            )
        else:
            raise DataNotSupportedError(f"File {f} is not in a supported format.")

    return TableCollection(
        data_directory=data_directory,
        data=loaded_files,
        general_description=general_description,
        data_dictionary=data_dictionary,
        use_cases=use_cases,
        discovery=None,
    )


def load_google_storage_files() -> TableCollection:
    pass


def load_csv(
    file_path: str,
    general_description: Optional[str] = None,
    data_dictionary: Optional[Dict[str, str]] = None,
    use_cases: Optional[List[str]] = None,
    allowed_columns: Optional[List[str]] = None,
    config: Dict[str, Any] = dict(),
) -> Table:
    
    if config.get("usecols") is None:
        config["usecols"] = allowed_columns
        
    data: pd.DataFrame = pd.read_csv(file_path, **config)

    diff = set(config["usecols"]).difference(set(data.columns))
    if len(diff) > 0:
        warnings.warn(f"file {file_path} was given columns {config["usecols"]}, but they do not exist in the data.")

    name: str = file_path.split("/")[-1] if "/" in file_path else file_path

    return Table(
        name=name,
        data=data,
        general_description=general_description,
        data_dictionary=data_dictionary,
        use_cases=use_cases,
        discovery=None
    )



def load_json(
    file_path: str,
    allowed_columns: Optional[List[str]] = None,
    config: Dict[str, Any] = dict(),
) -> Table:
    pd.read
    pass

def _check_files(files: Set[str]) -> bool:
    """
    Validate that all files in data directory are compatible. This should be ran before attempting to load directory.
    """
    valid_formats: List[str] = ["csv", "json"]
    bad_files: List[str] = [f for f in files if f.split(".")[-1] not in valid_formats]
    if len(bad_files) > 0: 
         raise DataNotSupportedError(f"File(s) {bad_files} is / are not in a supported format.")
    else:
        return True
       

