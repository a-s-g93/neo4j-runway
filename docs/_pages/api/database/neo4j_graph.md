---
permalink: /api/database/neo4j-graph/
title: Neo4jGraph
toc: true
toc_label: Neo4jGraph
toc_icon: "fa-solid fa-plane"
---
    from neo4j_runway.database import Neo4jGraph


 Handler for Neo4j graph interactions.

    Attributes
    ----------
    apoc_version : Union[str, None]
        The APOC version present in the database.
    database : Union[str, None]
        The database name to run queries against in the
        Neo4j instance.
    database_edition : str
        The edition of the Neo4j instance.
    database_version : str
        The Neo4j version of the Neo4j instance.
    driver : GraphDatabase.Driver
        The driver used to communicate with Neo4j.
        Constructed from credentials provided to the
        constructor.
    schema : Union[Dict[str, Any], None]
        The database schema gathered from APOC.meta.schema



## Class Methods


### __init__
Constructor for the Neo4jGraph.

    Parameters
    ----------
    username : Optional[str], optional
        Neo4j username. If not provided, will check
        NEO4J_USERNAME env variable. By default None
    password : Optional[str], optional
        Neo4j password. If not provided, will check
        NEO4J_PASSWORD env variable. By default None
    uri : Optional[str], optional
        Neo4j uri. If not provided, will check NEO4J_URI env
        variable. By default None
    database : Optional[str], optional
        Neo4j database to connect to. If not provided, will
        check NEO4J_DATABASE env variable. By default None
    driver_config : Dict[str, Any], optional
        Any additional configuration to provide the driver,
        by default dict()


### refresh_schema
Refresh the graph schema via APOC from the database.

    Raises
    ------
    APOCNotInstalledError
        If APOC is not installed on the Neo4j instance.

    Returns
    -------
    Dict[str, Any]
        The schema in APOC format, if APOC is present on
        database


### verify
Verify connection and authentication.

    Returns
    -------
    Dict[str, Any]
        Whether connection is successful and any messages.



## Class Properties


### schema
The database schema provided by apoc.meta.schema

    Returns
    -------
    Dict[str, Any]
        The schema.

