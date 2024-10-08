---
permalink: /api/utils/data/table-collection/
title: TableCollection
toc: true
toc_label: TableCollection
toc_icon: "fa-solid fa-plane"
---

    from neo4j_runway.utils.data import TableCollection



 A container for all data to be used in graph data modeling.
        This class will handle data in Table objects.

    Attributes
    ----------
    data_directory : str
        The directory where all data is found.
    tables : List[Table]
        A list of all Tables to be used in graph data
        modeling.
    general_description : str
        A general description of the data.
    data_dictionary : Dict[str, Any], optional
        A dictionary with file names as keys. Each key
        contains a dictionary containing a description of
        each column in the file that is available for data
        modeling.
    use_cases : Optional[List[str]], optional
        Any use cases that the graph data model should
        address.
    discovery : Optional[DiscoveryContent], optional
        Any insights gathered about the data. This is
        contained within the DiscoveryContent class.



## Class Methods


### __init__
A container for all data to be used in graph data
        modeling. This class will handle data in Table
        objects.

    Parameters
    ----------
    data_directory : str
        The directory where all data is found.
    tables : List[Table]
        A list of all Tables to be used in graph data
        modeling.
    general_description : str
        A general description of the data, by default None
    data_dictionary : Optional[Dict[str, str]], optional
        A dictionary with file names as keys. Each key
        contains a dictionary containing a description of
        each column in the file that is available for data
        modeling.
        Only columns identified here will be considered for
        inclusion in the data model. By default None
    use_cases : Optional[List[str]], optional
        Any use cases that the graph data model should
        address, by default None
    discovery : Optional[str], optional
    Any insights gathered about the data as a whole. By
        default None


### get_pandas_summary
A String containing all Pandas summaries generated for
        the contained Tables.

    Parameters
    ----------
    ignore_files : List[str], optional
        Any files to ignore, by default list()

    Returns
    -------
    str
        The Pandas summaries formatted into a String.


### to_markdown
Write the generated discovery to a Markdown file.

    Parameters
    ----------
    file_dir : str, optional
        The file directory to write to, by default "./"
    file_name : str, optional
        The name of the file, by default "discovery.md"


### to_txt
Write the generated discovery to a .txt file.

    Parameters
    ----------
    file_dir : str, optional
        The file directory to write to, by default "./"
    file_name : str, optional
        The name of the file, by default "discovery.txt"



## Class Properties


### pretty_use_cases
Format the use cases in a more readable format.

    Returns
    -------
    str
        The formatted use cases as a String.


### size
The number of Tables in the collection.

    Returns
    -------
    int
        The count of Tables.


### sub_discoveries
All unique sub discoveries generated by the Discovery
        module.

    Returns
    -------
    List[str]
        The sub discoveries.


### table_dict
A dictionary of Table name to Table.

    Returns
    -------
    Dict[str, Table]
        The dictionary.
