from typing import Any, Dict, Optional

import yaml


def load_data_dictionary_from_yaml(file_path: str) -> Dict[str, Any]:
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

    return _format_yaml_contents(loaded_yaml)


def _format_yaml_contents(yaml_contents: Dict[str, Any]) -> Dict[str, Any]:
    res = dict()
    single: bool = len(yaml_contents["files"]) == 1
    alias: Optional[str]
    ignore: bool

    if not single:
        for f in yaml_contents["files"]:
            sub_data_dict = dict()
            for col in f.get("columns", list()):
                alias = col.get("alias", None)
                ignore = col.get("ignore", False)
                desc: str = (
                    col.get("desc", "")
                    + ((" Has alias: " + alias) if alias is not None else "")
                    + (" | ignore" if ignore else "")
                )
                sub_data_dict.update({col["name"]: desc})
            res[f["name"]] = sub_data_dict
    else:
        f = yaml_contents["files"][0]
        # res = {d["name"]: d["desc"] for d in f["columns"]}
        for col in f.get("columns", list()):
            alias = col.get("alias", None)
            ignore = col.get("ignore", False)
            desc = (
                col.get("desc", "")
                + ((" Has alias: " + alias) if alias is not None else "")
                + (" | ignore" if ignore else "")
            )
            res.update({col["name"]: desc})

    return res
