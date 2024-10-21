---
permalink: /api/data-model/
title: DataModel
toc: true
toc_label: DataModel
toc_icon: "fa-solid fa-plane"
---

    from neo4j_runway import DataModel

This is the core data model class of Neo4j Runway. All imported data models will be converted to this data model format.


 The standard Graph Data Model representation in Neo4j
        Runway.

    Attributes
    ----------
    nodes : List[Node]
        A list of the nodes in the data model.
    relationships : List[Relationship]
        A list of the relationships in the data model.
    metadata: Optional[Dict[str, Any]]
        Metadata from an import source such as Solutions
        Workbench.



## Class Methods


### advanced_validation



### get_schema
Get the data model schema.

    Parameters
    ----------
    verbose : bool, optional
        Whether to provide more detail, by default True
    neo4j_typing : bool, optional
        Whether to use Neo4j types instead of Python types,
        by default False
    print_schema : bool, optional
        Whether to auto print the schema, by default False

    Returns
    -------
    str
        The schema


### to_arrows
Output the data model to arrows compatible JSON file.

    Parameters
    ----------
    file_path : str, optional
        The file path to write if write_file = True, by
        default "data-model.json"
    write_file : bool, optional
        Whether to write the file, by default True

    Returns
    -------
    ArrowsDataModel
        A representation of the data model in arrows.app
        format.


### to_json
Output the data model to a json file.

    Parameters
    ----------
    file_path : str, optional
        The file path to write, by default "data-model.json"

    Returns
    -------
    Dict[str, any]
        A Python dictionary version of the json.


### to_solutions_workbench
Output the data model to Solutions Workbench compatible
        JSON file.

    Parameters
    ----------
    file_path : str, optional
        The file path to write if write_file = True, by
        default "data-model.json"
    write_file : bool, optional
        Whether to write the file, by default True

    Returns
    -------
    SolutionsWorkbenchDataModel
        A representation of the data model in Solutions
        Workbench format.


### to_yaml
Output the data model to a yaml file and String.

    Parameters
    ----------
    file_path : str, optional
        The file path to write if write_file = True, by
        default "data-model.yaml"
    write_file : bool, optional
        Whether to write the file, by default True

    Returns
    -------
    str
        A String representation of the yaml file.


### visualize
Visualize the data model using Graphviz. Requires that
        Graphviz is installed.

    Parameters
    ----------
    detail_level : Literal[1, 2, 3]
        The level of detail to include in the visual

        1: Node labels and Relationship types only

        2: Node labels, Relationship types and basic
        Property info

        3: Node labels, Relationship types and all Property
        info
    neo4j_typing : bool, optional
        Whether to use Neo4j types instead of Python types,
        by default False

    Returns
    -------
    Digraph
        The dot for visualization


### from_arrows
Construct a DataModel from an arrows data model JSON
        file.

    Parameters
    ----------
    file_path : str
        The location and name of the arrows.app JSON file to
        import.

    Raises
    ------
    InvalidArrowsDataModelError
        If the json file is unable to be parsed.

    Returns
    -------
    DataModel
        An instance of a DataModel.


### from_solutions_workbench
Construct a DataModel from a Solutions Workbench data
        model JSON file.

    Parameters
    ----------
    file_path : str
        The location and name of the Solutions Workbench
        JSON file to import.

    Raises
    ------
    InvalidSolutionsWorkbenchDataModelError
        If the json file is unable to be parsed.

    Returns
    -------
    DataModel
        An instance of a DataModel.



## Class Properties


### node_dict
Returns a dictionary of node label to Node.

    Returns
    -------
    Dict[str, Node]
        A dictionary with node label keys and Node values.


### node_labels
Returns a list of node labels.

    Returns
    -------
    List[str]
        A list of node labels.


### relationship_dict
Returns a dictionary of relationship type to
        Relationships.

    Returns
    -------
    Dict[str, Relationship]
        A dictionary with relationship type keys and
        Relationship values.


### relationship_types
Returns a list of relationship types.

    Returns
    -------
    List[str]
        A list of relationship types.
