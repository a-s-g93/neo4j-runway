from typing import Dict, List, Optional

import pandas as pd


class Table:
    name: str
    file_path: str
    data: pd.DataFrame
    general_description: Optional[str] = None
    data_dictionary: Optional[Dict[str, str]] = None
    use_cases: Optional[List[str]] = None
    discovery: Optional[str] = None

    def __init__(
        self,
        name: str,
        file_path: str,
        data: pd.DataFrame,
        general_description: Optional[str] = None,
        data_dictionary: Optional[Dict[str, str]] = None,
        use_cases: Optional[List[str]] = None,
        discovery: Optional[str] = None,
    ) -> None:
        self.name = name
        self.file_path = file_path
        self.data = data
        self.general_description = general_description
        self.data_dictionary = data_dictionary
        self.use_cases = use_cases
        self.discovery = discovery


class TableCollection:
    data_directory: str
    data: List[Table]
    general_description: Optional[str] = None
    data_dictionary: Optional[Dict[str, str]] = None
    use_cases: Optional[List[str]] = None
    discovery: Optional[str] = None
