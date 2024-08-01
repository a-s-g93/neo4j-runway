---
permalink: /api/code-generator/standard-cypher-code-generator/
title: StandardCypherCodeGenerator
toc: true
toc_label: StandardCypherCodeGenerator
toc_icon: "fa-solid fa-plane"
---

    from neo4j_runway.code_generation import StandardCypherCodeGenerator


 A class for generating standard plain old Cypher code.

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
        (True), or infer types during ingestion (False).



## Class Methods


### __init__
This is the base class for code generation. All code
        generation classes must inherit from this class.

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

