---
permalink: /api/code-generator/load-csv-code-generator/
title: LoadCSVCodeGenerator
toc: true
toc_label: LoadCSVCodeGenerator
toc_icon: "fa-solid fa-plane"
---

    from neo4j_runway.code_generation import LoadCSVCodeGenerator


 Class responsible for generating the LOAD CSV code.

    Attributes
    ----------
    data_model : DataModel
        The data model to base ingestion code on.
    file_directory : str, optional
        Where the files are located.
    file_output_directory : str, optional
        The location that generated files should be saved
        to.
    csv_name : str, optional
        The name of the CSV file. If more than one CSV is
        used, this arg should not be provided.
        CSV file names should be included within the data
        model.
    strict_typing : bool, optional
        Whether to use the types declared in the data model
        (True), or infer types during ingestion (False). By
        default True
    batch_size : int, optional
        The desired batch size.
    method : str, optional
        The method that LOAD CSV will be run. Must be either
        "api" or "browser".



## Class Methods


### __init__
Class responsible for generating the LOAD CSV code.

    Parameters
    ----------
    data_model : DataModel
        The data model to base ingestion code on.
    file_directory : str, optional
        Where the files are located. By default = "./"
    file_output_directory : str, optional
        The location that generated files should be saved
        to, by default "./"
    csv_name : str, optional
        The name of the CSV file. If more than one CSV is
        used, this arg should not be provided.
        CSV file names should be included within the data
        model. By default = ""
    strict_typing : bool, optional
        Whether to use the types declared in the data model
        (True), or infer types during ingestion (False). By
        default True
    batch_size : int, optional
        The desired batch size, by default 100
    method : str, optional
        The method that LOAD CSV will be run. Must be either
        "api" or "browser". By default "api"


### generate_constraints_file
Genreate a .cypher file containing the generated
        constraints.

    Parameters
    ----------
    file_name : str, optional
        Name of the file, by default "constraints.cypher"


### generate_constraints_string
Generate a single String representation of all
        constraints.

    Returns
    -------
    str
        The constraints in String format.


### generate_cypher_file
Generate a .cypher file containing the generated
        ingestion code.

    Parameters
    ----------
    file_name : str, optional
        Name of the file, by default "ingest_code.cypher"


### generate_cypher_string
Generate a single String representation of all ingestion
        code.

    Returns
    -------
    str
        The Cypher in String format.


### generate_load_csv_cypher_file
Generate the LOAD CSV Cypher file.

    Parameters
    ----------
    file_name : str, optional
        The file name.


### generate_load_csv_cypher_string
Generate the load_csv cypher in string format.

    Returns
    -------
    str
        The LOAD CSV Cypher in String format.

