from typing import Any, Dict, List, Optional

from ...discovery.discovery_content import DiscoveryContent
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
    general_description : str
        A general description of the data.
    data_dictionary : Dict[str, Any], optional
        A dictionary with file names as keys. Each key contains a dictionary containing a description of each column in the file that is available for data modeling.
    use_cases : Optional[List[str]], optional
        Any use cases that the graph data model should address.
    discovery : Optional[DiscoveryContent], optional
        Any insights gathered about the data. This is contained within the DiscoveryContent class.
    """

    data_directory: str
    data: List[Table]
    general_description: str = ""
    data_dictionary: Dict[str, Any] = dict()
    use_cases: Optional[List[str]] = None
    discovery: Optional[str] = None

    def __init__(
        self,
        data_directory: str,
        data: List[Table],
        general_description: str = "",
        data_dictionary: Dict[str, Any] = dict(),
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
        general_description : str
            A general description of the data, by default None
        data_dictionary : Optional[Dict[str, str]], optional
            A dictionary with file names as keys. Each key contains a dictionary containing a description of each column in the file that is available for data modeling.
            Only columns identified here will be considered for inclusion in the data model. By default None
        use_cases : Optional[List[str]], optional
            Any use cases that the graph data model should address, by default None
        discovery : Optional[str], optional
        Any insights gathered about the data as a whole. By default = None
        """
        self.data_directory = data_directory
        self.data = data
        self.general_description = general_description
        self.data_dictionary = data_dictionary
        self.use_cases = use_cases
        self.discovery = discovery

    def __len__(self) -> int:
        return len(self.data)

    @property
    def size(self) -> int:
        """
        The number of Tables in the collection.

        Returns
        -------
        int
            The count of Tables.
        """

        return self.__len__()

    @property
    def table_dict(self) -> Dict[str, Table]:
        return {t.name: t for t in self.data}

    @property
    def pretty_use_cases(self) -> str:
        """
        Format the use cases in a more readable format.

        Returns
        -------
        str
            The formatted use cases as a String.
        """

        if self.use_cases is None:
            return ""

        res = ""
        for uc in self.use_cases:
            res += "* " + uc + "\n"
        return res

    def get_pandas_summary(self, ignore_files: List[str] = list()) -> str:
        # priority:
        #   custom batches
        #   batch size & ignore files

        response = (
            "Here are Summary Statistics generated with the Pandas Python library"
        )
        for t in self.data:
            if t.name not in ignore_files and t.discovery_content is not None:
                response += (
                    f"\n\n### {t.name}\n{t.discovery_content.pandas_response}\n\n-----"
                )

        return response