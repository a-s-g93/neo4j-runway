"""
This file contains misc functions for Cypher generation.
"""

from typing import List, Union


def format_pyingest_pre_or_post_ingest_code(data: Union[str, List[str], None]) -> str:
    """
    Format the given post ingest code into a String to be injected into the
    PyIngest yaml file.
    """

    if isinstance(data, str) and ".cypher" not in data and ".cql" not in data:
        res = ""
        for cql in data.split(";")[:-1]:
            cql_formatted = cql.lstrip().replace("\n", "\n    ")
            res += f"  - {cql_formatted}\n"
        return res
    elif isinstance(data, str) and (".cypher" in data or ".cql" in data):
        with open(data, "r") as f:
            cql_file = f.read()
        res = ""
        for cql in cql_file.split(";")[:-1]:
            cql_formatted = cql.lstrip().replace("\n", "\n    ")
            res += f"  - {cql_formatted}\n"
        return res

    elif isinstance(data, list):
        res = ""
        for cql in data:
            cql_formatted = cql.lstrip().replace("\n", "\n    ")
            res += f"  - {cql_formatted}\n"
        return res
    else:
        raise ValueError(f"Unable to parse ingest code. data: {data}")


def format_pyneoinstance_pre_or_post_ingest_code(
    data: Union[str, List[str], None],
) -> List[str]:
    """
    Format the given post ingest code into a String to be injected into the
    PyNeoInstance yaml file.
    """

    if isinstance(data, str) and ".cypher" not in data and ".cql" not in data:
        # print([x.lstrip().replace("\n", "\n    ") for x in data.split(";")[:-1]])
        return [x.strip() for x in data.split(";")[:-1]]
        # return data.split(";")[:-1]

    elif isinstance(data, str) and (".cypher" in data or ".cql" in data):
        with open(data, "r") as f:
            cql_file = f.read()
        return cql_file.split(";")[:-1]

    elif isinstance(data, list):
        return data
    else:
        raise ValueError(f"Unable to parse ingest code. data: {data}")
