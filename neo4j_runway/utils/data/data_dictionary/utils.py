from typing import Any, Dict, List, Optional

import pandas as pd
import yaml

from ..._utils.dictionary import get_dictionary_depth
from .column import Column
from .data_dictionary import DataDictionary
from .table_schema import TableSchema


def load_data_dictionary_from_yaml(file_path: str) -> DataDictionary:
    """
    Load a data dictionary stored in a yaml file. Can either be a multi or single file data dictionary.

    Parameters
    ----------
    file_path : str
        The location of the file.

    Returns
    -------
    Dict[str, Any]
        The data dictionary as a Python dictionary.
    """

    with open(file_path, "r") as f:
        content = f.read()

    loaded_yaml = yaml.safe_load(content)

    values = _format_yaml_contents(loaded_yaml)

    return DataDictionary.model_validate(
        {"table_schemas": values.get("table_schema_list")},
        context={"column_names": values.get("all_property_names")},
    )


def _format_yaml_contents(yaml_contents: Dict[str, Any]) -> Dict[str, Any]:
    assert (
        yaml_contents.get("files") is not None
    ), "data dictionary yaml file must have 'files' key header."

    table_schema_list = list()
    all_property_names = set()

    for table_schema in yaml_contents["files"]:
        table_schema_dict = {"name": table_schema.get("name")}
        columns_list = list()
        for col in table_schema.get("columns", list()):
            column_dict = dict()
            column_dict.update({"name": col.get("name")})
            column_dict.update(
                {"description": col.get("desc") or col.get("description")}
            )
            column_dict.update({"python_type": col.get("python_type")})
            column_dict.update(
                {"aliases": col.get("aliases") or _get_aliases_from_alias(col_dict=col)}
            )

            if col.get("primary_key") is not None:
                column_dict.update({"primary_key": col.get("primary_key")})
            if col.get("foreign_key") is not None:
                column_dict.update({"foreign_key": col.get("foreign_key")})
            if col.get("ignore") is not None:
                column_dict.update({"ignore": col.get("ignore")})
            if col.get("nullable") is not None:
                column_dict.update({"nullable": col.get("nullable")})

            columns_list.append(column_dict)

            all_property_names.add(col.get("name"))
            all_property_names.add(col.get("aliases"))
            all_property_names.add(col.get("alias"))

        table_schema_dict.update({"columns": columns_list})
        table_schema_list.append(table_schema_dict)

    return {
        "table_schema_list": table_schema_list,
        "all_property_names": list(all_property_names),
    }


def _get_aliases_from_alias(col_dict: Dict[str, Any]) -> Optional[List[str]]:
    if col_dict.get("alias") is not None:
        aliases = col_dict.get("alias")
        if not isinstance(aliases, list) and aliases is not None:
            return [str(aliases)]
        return aliases
    return None


def load_data_dictionary_from_compact_python_dictionary(
    python_dictionary: Dict[str, Any], file_name: str = "file"
) -> DataDictionary:
    """
    Load a Python dictionary representation of the data dictionary as a `DataDictionary` object.

    Parameters
    ----------
    python_dictionary : Dict[str, Any]
        The input dictionary. Must adhere to the following structure:
        multi or single file input
        {
        file_name: {
            column_name: column_description, ...
            }, ...
        }
        OR for single file only
        {
        column_name>: <column description>, ...
        }
    file_name : str, optional
        The file name, if providing a single file data dictionary, by default 'file'

    Returns
    -------
    DataDictionary
        The `DataDictionary` object.
    """

    depth = get_dictionary_depth(python_dictionary)

    if depth == 1:
        return DataDictionary.model_validate(
            {
                "table_schemas": [
                    {
                        "name": file_name,
                        "columns": [
                            {"name": name, "description": desc}
                            for name, desc in python_dictionary.items()
                        ],
                    }
                ]
            }
        )
    elif depth == 2:
        return DataDictionary.model_validate(
            {
                "table_schemas": [
                    {
                        "name": file_name,
                        "columns": [
                            {"name": name, "description": desc}
                            for name, desc in table_schema.items()
                        ],
                    }
                    for file_name, table_schema in python_dictionary.items()
                ]
            }
        )
    else:
        raise ValueError(
            "Unable to parse the provided `python_dictionary` into a `DataDictionary` object."
        )


def load_table_schema_from_compact_python_dictionary(
    python_dictionary: Dict[str, Any], file_name: str = "file"
) -> TableSchema:
    """
    Load a Python dictionary representation of the table schema as a `TableSchema` object.

    Parameters
    ----------
    python_dictionary : Dict[str, Any]
        The input dictionary. Must adhere to the following structure:
        {
        <file name>: {
            <column name>: <column description>, ...
            }
        }
        OR
        {
        <column name>: <column description>, ...
        }
    file_name : str, optional
        The file name, by default 'file'

    Returns
    -------
    TableSchema
        The `TableSchema` object.
    """

    depth = get_dictionary_depth(python_dictionary)

    if depth == 1:
        return TableSchema.model_validate(
            {
                "name": file_name,
                "columns": [
                    {"name": name, "description": desc}
                    for name, desc in python_dictionary.items()
                ],
            }
        )
    elif depth == 2:
        file_name = list(python_dictionary.keys())[0]
        col_dict: Dict[str, str] = list(python_dictionary.values())[0]
        return TableSchema.model_validate(
            {
                "name": file_name,
                "columns": [
                    {"name": name, "description": desc}
                    for name, desc in col_dict.items()
                ],
            }
        )
    else:
        raise ValueError(
            "Unable to parse the provided `python_dictionary` into a `TableSchema` object."
        )


def create_data_dictionary_from_pandas_dataframe(
    dataframe: pd.DataFrame, name: str = "file"
) -> DataDictionary:
    """
    Create a `DataDictionary` from the columns of a provided DataFrame.

    Parameters
    ----------
    dataframe : pd.DataFrame
        The Pandas DataFrame

    Returns
    -------
    DataDictionary
    """

    table_schema = TableSchema(
        name=name, columns=[Column(name=c) for c in list(dataframe.columns)]
    )
    return DataDictionary(table_schemas=[table_schema])
