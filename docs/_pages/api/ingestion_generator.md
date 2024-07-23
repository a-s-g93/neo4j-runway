---
permalink: /api/ingestion-generator/
toc: true
toc_label: IngestionGenerator
toc_icon: "fa-solid fa-plane"
---
# IngestionGenerator


## Class Methods


### __init__
Class responsible for generating the ingestion code.

    Attributes
    ----------
    data_model : DataModel
        The data model to base ingestion code on.
    csv_name : str, optional
        The CSV containing the data. If data is contained in
        multiple CSVs,
        then this should be "" and CSVs noted in the data
        model, by default ""
    username : Union[str, None], optional
        The username used to connect to Neo4j, by default
        None
    password : Union[str, None], optional
        The password used to connect to Neo4j, by default
        None
    uri : Union[str, None], optional
        The uri of the Neo4j instance, by default None
    database : Union[str, None], optional
        The database within the Neo4j instance to load the
        data, by default None
    csv_dir : str, optional
        The location of the CSV file(s), by default ""
    file_output_dir : str, optional
        The location that generated files should be saved
        to, by default ""


### generate_constraints_cypher_file
Generate the Constraints cypher file.

    Parameters
    ----------
    file_name : str, optional
        Name of the file, by default "constraints"

    Returns
    ----------
    None


### generate_constraints_cypher_string
Generate the Constraints cypher file in string format.

    Returns
    ----------
    str
        The constraints Cypher in String format.


### generate_load_csv_file
Generate the LOAD CSV Cypher file.

    Parameters
    ----------
    file_name : str, optional
        Name of the file, by default "load_csv"
    batch_size : int, optional
        The desired batch size, by default 100
    method : str, optional
        The method that LOAD CSV will be run. Must be either
        "api" or "browser". By default "api"
    strict_typing: bool, optional
        Whether to use the types declared in the data model
        (True), or infer types during ingestion (False). By
        defaut True

    Returns
    ----------
    None


### generate_load_csv_string
Generate the load_csv cypher in string format.

    Parameters
    ----------
    batch_size : int, optional
        The desired batch size, by default 100
    method : str, optional
        The method that LOAD CSV will be run. Must be either
        "api" or "browser". By default "api"
    strict_typing: bool, optional
        Whether to use the types declared in the data model
        (True), or infer types during ingestion (False). By
        defaut True

    Returns
    ----------
    str
        The LOAD CSV Cypher in String format.


### generate_pyingest_yaml_file
Generate the PyIngest YAML config file.

    Parameters
    ----------
    file_name : str, optional
        Name of the file, by default "pyingest_config"
    global_batch_size : int, optional
        The desired batch size for all files, by default 100
    global_field_separator: str, optional
        The separator used for all CSV files, by default ","
    pyingest_file_config: Dict[str, Any], optional
        A dictionary containing individual file parameters.
        Supported parameters are: batch_size <int>,
        skip_records <int>, skip_file <int> and
        field_separator <str>
    post_ingest_code : Union[str, List[str], None], optional
        Code to be run after all data is ingested.
        Can be either a String of cypher code, .cypher file
        filepath or list of cypher commands.
        Individual Cypher queries should be separated by a
        ';'.
    strict_typing : bool, optional
        Whether to use the types declared in the data model
        (True), or infer types during ingestion (False). By
        default True

    Returns
    ----------
    None


### generate_pyingest_yaml_string
Generate the PyIngest yaml in string format.

    Parameters
    ----------
    global_batch_size : int, optional
        The desired batch size for all files, by default 100
    global_field_separator: str, optional
        The separator used for all CSV files, by default ","
    pyingest_file_config: Dict[str, Any], optional
        A dictionary containing individual file parameters.
        Supported parameters are: batch_size <int>,
        skip_records <int>, skip_file <int> and
        field_separator <str>
    post_ingest_code : Union[str, List[str], None], optional
        Code to be run after all data is ingested.
        Can be either a String of cypher code, .cypher file
        filepath or list of cypher commands.
        Individual Cypher queries should be separated by a
        ';'.
    strict_typing : bool, optional
        Whether to use the types declared in the data model
        (True), or infer types during ingestion (False). By
        defaut True

    Returns
    ----------
    str
        The yaml configuration in String format.

