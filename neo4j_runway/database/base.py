from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseGraph(ABC):
    """
    Base class for all Graph modules.
    """

    def __init__(self, driver: Any, version: str) -> None:
        """
        Base class for all Graph modules.

        Parameters
        ----------
        driver : Any
            Thhe driver used to handle communication with the database.
        version : str
            The database version.
        """

    @abstractmethod
    def refresh_schema(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def _get_database_version(self) -> str:
        pass
