from typing import Any, Dict, List, Optional

from pydantic import BaseModel, field_validator

from .column import Column


class TableSchema(BaseModel):
    """
    The table schema for a relational table.

    Attributes
    ----------
    columns : List[Column]
        A list of columns in the table.
    name : str
        The table name.
    """

    columns: List[Column]
    name: str

    @field_validator("columns")
    def validate_columns(cls, columns: List[Column]) -> List[Column]:
        primary_keys = [c.name for c in columns if c.primary_key]
        if len(primary_keys) > 1:
            raise ValueError(
                f"Only 1 column may have attribute `primary_key` = True. Choose one of the following: {primary_keys}"
            )
        return columns

    @property
    def columns_dict(self) -> Dict[str, Column]:
        """
        A dictionary of column name keys and `Column` object values.

        Returns
        -------
        Dict[str, Column]
            The dictionary.
        """

        return {c.name: c for c in self.columns}

    @property
    def column_names(self) -> List[str]:
        """
        The column names in the table.

        Returns
        -------
        List[str]
            A list of column names.
        """

        return [c.name for c in self.columns]

    @property
    def primary_key(self) -> Optional[Column]:
        """
        The primary key column, if it exists.

        Returns
        -------
        Optional[Column]
            The primary key column, if it exists or `None`.
        """
        pk = [c for c in self.columns if c.primary_key]
        if pk:
            return pk[0]
        else:
            return None

    @property
    def foreign_keys(self) -> List[Column]:
        """
        The foreign key columns.

        Returns
        -------
        Column
            The foreign key columns.
        """

        return [c for c in self.columns if c.foreign_key]

    @property
    def compact_dict(self) -> Dict[str, Any]:
        """
        Compact representation of the `TableSchema` information.

        Returns
        -------
        Dict[str, Any]
            A dictionary.
        """

        compact_info: Dict[str, str] = dict()
        [compact_info.update(c.compact_dict) for c in self.columns]
        return {self.name: compact_info}

    def get_column(self, column_name: str) -> Optional[Column]:
        """
        Retrieve a `Column` object by name.

        Parameters
        ----------
        column_name : str
            The name of the column.

        Returns
        -------
        Optional[Column]
            A `Column` object if it exists, or None
        """

        return self.columns_dict.get(column_name)

    def get_description(self, column_name: str) -> str:
        """
        Retrieve the description for a column. If there is no description, then return an empty string.

        Parameters
        ----------
        column_name : str
            The column name to search for in the table.

        Returns
        -------
        str
            A description of the column, if it exists.
        """

        col = self.columns_dict.get(column_name)
        if col is not None:
            return col.description or ""
        return ""
