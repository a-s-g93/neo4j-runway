---
permalink: /api/utils/data/data-loaders/
title: Data Loaders
toc: true
toc_label: Data Loaders
toc_icon: "fa-solid fa-plane"
---
## load_local_files

    from neo4j_runway.utils.data import load_local_files


A function to systematically load all files from a local
        directory. Currently supported file formats are:
        [csv, json, jsonl].

    Parameters
    ----------
    data_directory : str
        The directory containing all data.
    general_description : str
        A general description of the data, by default None
    data_dictionary : Dict[str, Any], optional
        A dictionary with file names as keys. Each key has a
        dictionary containing a description of each column
        in the file that is available for data modeling.
        Only columns identified here will be considered for
        inclusion in the data model. By default dict()
    use_cases : Optional[List[str]], optional
        Any use cases that the graph data model should
        address, by default None
    include_files: List[str], optional
        Any filres in the directory that should be included.
        Overwrites `ignored_files` arg. By default list()
    ignored_files : List[str], optional
        Any files in the directory that should be ignored.
        Will be overwritten if `include_files` arg is
        provided. By default list()
    config : Dict[str, Dict[str, Any]], optional
        A dictionary with file names as keys. Each key has a
        dictionary containing arguments to pass to the
        Pandas load_* function. By default dict()

    Returns
    -------
    TableCollection
        The container for all loaded data.

    Raises
    ------
    DataNotSupportedError
        If an attempt is made to load an unsupported file.


## load_data_dictionary_from_yaml

    from neo4j_runway.utils.data import load_data_dictionary_from_yaml


Load a data dictionary stored in a yaml file. Can either
        be a multi or single file data dictionary.

    Parameters
    ----------
    file_path : str
        The location of the file.

    Returns
    -------
    Dict[str, Any]
        The data dictionary as a Python dictionary.
