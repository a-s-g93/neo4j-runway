---
permalink: /api/inputs/
title: UserInput
toc: true
toc_label: UserInput
toc_icon: "fa-solid fa-plane"
---

    from neo4j_runway import UserInput


 A container for user provided information about the data.

    Attributes
    ----------
    general_description : str, optional
        A general description of the CSV data.
    data_dictionary : Dict[str, str], optional
        A mapping of the desired columns to their
        descriptions.
        If multi-file, then each file name should contain
        it's own sub dictionary.
        The keys of this argument will determine which CSV
        columns are
        evaluated in discovery and used to generate a data
        model.
    use_cases : List[str], optional
        A list of use cases that the final data model should
        be able to answer.



## Class Methods


### __init__
A container for user provided information about the
        data.

    Parameters
    ----------
    general_description : str, optional
        A general description of the CSV data, by default =
        ""
    data_dictionary : Dict[str, str], optional
        A mapping of the desired columns to their
        descriptions.
        If multi-file, then each file name should contain
        it's own sub dictionary.
        The leaf values of this argument will determine
        which columns are
        evaluated in discovery and used to generate a data
        model.
    use_cases : List[str], optional
        A list of use cases that the final data model should
        be able to answer.



## Class Properties


### allowed_columns
The allowed columns.

    Returns
    -------
    Union[List[str], Dict[str, List[str]]]
        single file : A list of columns from the DataFrame.
        Multi file  : a dictionary with keys of file names
        and A list of columns for each file.


### is_multifile
Whether the data dictionary covers multiple files.

    Returns
    -------
    bool


### pretty_use_cases
Format the use cases in a more readable format.

    Returns
    -------
    str
        The formatted use cases as a String.
