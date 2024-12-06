from typing import Dict, List, Optional, TypedDict

from ..utils.data.data_dictionary.data_dictionary import DataDictionary


class Context(TypedDict):
    """
    Context for `DataModel` validation.

    Attributes
    ----------
    data_dictionary : Dict[str, Any]
        The data dictionary containing files, columns and descriptions.
    valid_columns : Dict[str, List[str]]
        The valid columns allowed per file.
    enforce_uniqueness : bool
        Whether to enforce Node uniqueness
    apply_neo4j_naming_conventions : bool
        Whether to apply Neo4j naming conventions
    allow_duplicate_column_mappings : bool
        Whether to allow a column to be mapped to many Properties
    allow_parallel_relationships : bool
        Whether to allow parallel (same direction or reverse) relationships in the data model
    """

    data_dictionary: DataDictionary
    valid_columns: Dict[str, List[str]]
    enforce_uniqueness: bool
    apply_neo4j_naming_conventions: bool
    allow_duplicate_column_mappings: bool
    allow_parallel_relationships: bool


def create_context(
    data_dictionary: DataDictionary,
    valid_columns: Optional[Dict[str, List[str]]] = None,
    enforce_uniqueness: bool = True,
    apply_neo4j_naming_conventions: bool = True,
    allow_duplicate_column_mappings: bool = False,
    allow_parallel_relationships: bool = False,
) -> Context:
    """
    Construct the Context for `DataModel` validation.

    Parameters
    ----------
    data_dictionary : DataDictionary
        The data dictionary containing files, columns and descriptions.
    valid_columns : Optional[Dict[str, List[str]]], optional
        The valid columns allowed per file, by default None
    enforce_uniqueness : bool, optional
        Whether to enforce Node uniqueness, by default True
    apply_neo4j_naming_conventions : bool, optional
        Whether to apply Neo4j naming conventions, by default True
    allow_duplicate_column_mappings : bool, optional
        Whether to allow a column to be mapped to many Properties, by default False
    allow_parallel_relationships : bool, optional
        Whether to allow parallel (same direction or reverse) relationships in the data model, by default False

    Returns
    -------
    Context
        The context for validation.
    """

    assert isinstance(
        data_dictionary, DataDictionary
    ), "Must provide a `DataDictionary` object."

    if valid_columns is None:
        valid_columns = data_dictionary.table_column_names_dict

    return Context(
        data_dictionary=data_dictionary,
        valid_columns=valid_columns,
        allow_duplicate_column_mappings=allow_duplicate_column_mappings,
        apply_neo4j_naming_conventions=apply_neo4j_naming_conventions,
        enforce_uniqueness=enforce_uniqueness,
        allow_parallel_relationships=allow_parallel_relationships,
    )
