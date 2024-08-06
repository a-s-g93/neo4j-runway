from typing import Dict, List, Optional

from .table import Table


class TableCollection:
    """
    A container for all data to be used in graph data modeling. This class will handle data in Table objects.

    Attributes
    ----------
    data_directory : str
        The directory where all data is found.
    data : List[Table]
        A list of all Tables to be used in graph data modeling.
    general_description : Optional[str], optional
        A general description of the data.
    data_dictionary : Dict[str, Dict[str, str]], optional
        A dictionary with file names as keys. Each key contains a dictionary containing a description of each column in the file that is available for data modeling.
    use_cases : Optional[List[str]], optional
        Any use cases that the graph data model should address.
    discovery : Optional[str], optional
        Any insights gathered about the data. Ideally this is text from the Discovery module.
    """

    data_directory: str
    data: List[Table]
    general_description: Optional[str] = None
    data_dictionary: Dict[str, Dict[str, str]] = dict()
    use_cases: Optional[List[str]] = None
    discovery: Optional[str] = None

    def __init__(
        self,
        data_directory: str,
        data: List[Table],
        general_description: Optional[str] = None,
        data_dictionary: Dict[str, Dict[str, str]] = dict(),
        use_cases: Optional[List[str]] = None,
        discovery: Optional[str] = None,
    ) -> None:
        """
        A container for all data to be used in graph data modeling. This class will handle data in Table objects.

        Parameters
        ----------
        data_directory : str
            The directory where all data is found.
        data : List[Table]
            A list of all Tables to be used in graph data modeling.
        general_description : Optional[str], optional
            A general description of the data, by default None
        data_dictionary : Optional[Dict[str, str]], optional
            A dictionary with file names as keys. Each key contains a dictionary containing a description of each column in the file that is available for data modeling.
            Only columns identified here will be considered for inclusion in the data model. By default None
        use_cases : Optional[List[str]], optional
            Any use cases that the graph data model should address, by default None
        discovery : Optional[str], optional
            Any insights gathered about the data. Ideally this is text from the Discovery module. By default None
        """
        self.data_directory = data_directory
        self.data = data
        self.general_description = general_description
        self.data_dictionary = data_dictionary
        self.use_cases = use_cases
        self.discovery = discovery
