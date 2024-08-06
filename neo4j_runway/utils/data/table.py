from typing import Dict, List, Optional

import pandas as pd


class Table:
    """
    A container for a Pandas DataFrame and its associated information.

    Attributes
    ----------
    name : str
        The name of the data file.
    file_path : str
        The full file path to the file.
    data : pd.DataFrame
        The data in Pandas DataFrame format.
    general_description : Optional[str], optional
        A general description of the data.
    data_dictionary : Dict[str, str], optional
        A description of each column that is available for data modeling. Only columns identified here will be considered for inclusion in the data model.
    use_cases : Optional[List[str]], optional
        Any use cases that the graph data model should address.
    discovery : Optional[str], optional
        Any insights gathered about the data. Ideally this is text from the Discovery module.
    """

    name: str
    file_path: str
    data: pd.DataFrame
    general_description: Optional[str] = None
    data_dictionary: Optional[Dict[str, str]] = dict()
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
        """
        A container for a Pandas DataFrame and its associated information.

        Parameters
        ----------
        name : str
            The name of the data file.
        file_path : str
            The full file path to the file.
        data : pd.DataFrame
            The data in Pandas DataFrame format.
        general_description : Optional[str], optional
            A general description of the data, by default None
        data_dictionary : Dict[str, str], optional
            A description of each column that is available for data modeling, by default dict()
        use_cases : Optional[List[str]], optional
            Any use cases that the graph data model should address, by default None
        discovery : Optional[str], optional
            Any insights gathered about the data. Ideally this is text from the Discovery module. By default None
        """
        self.name = name
        self.file_path = file_path
        self.data = data
        self.general_description = general_description
        self.data_dictionary = data_dictionary
        self.use_cases = use_cases
        self.discovery = discovery
