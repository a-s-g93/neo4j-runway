from typing import Any, Dict, List

from pydantic import BaseModel

from .column import Column
from .table_schema import TableSchema


class DataDictionary(BaseModel):
    table_schemas: List[TableSchema]

    @property
    def table_column_names_dict(self) -> Dict[str, List[str]]:
        """
        A dictionary with table name keys and column list values.

        Returns
        -------
        Dict[str, List[str]]
            The dictionary.
        """

        return {ts.name: ts.column_names for ts in self.table_schemas}

    @property
    def table_columns_dict(self) -> Dict[str, List[Column]]:
        """
        A dictionary with table name keys and `Column` list values.

        Returns
        -------
        Dict[str, List[Column]]
            The dictionary.
        """

        return {ts.name: ts.columns for ts in self.table_schemas}

    @property
    def compact_dict(self) -> Dict[str, Any]:
        """
        Compact representation of the `DataDictionary` information.

        Returns
        -------
        Dict[str, Any]
            A dictionary.
        """
        compact_info: Dict[str, str] = dict()
        [compact_info.update(ts.compact_dict) for ts in self.table_schemas]
        return compact_info
