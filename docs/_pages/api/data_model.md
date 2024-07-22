---
permalink: /api/data-model/
---
# DataModel
This is the core data model class of Neo4j Runway. All imported data models will be converted to this data model format. 


## Class Methods


__init__
---
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
        Workbench, by default None
    use_neo4j_naming_conventions : bool, optional
        Whether to convert labels, relationships and
        properties to Neo4j naming conventions, by default
        True


apply_neo4j_naming_conventions
---
Apply Neo4j naming conventions to all labels,
        relationships and properties in the data model.

    Returns
    -------
    None


to_arrows
---
Output the data model to arrows compatible JSON file.

    Parameters
    ----------
    file_name : str, optional
        The file name, by default "data-model"
    write_file : bool, optional
        Whether to write a file, by default True

    Returns
    -------
    ArrowsDataModel
        A representation of the data model in arrows.app
        format.


to_json
---
Output the data model to a JSON file.


to_solutions_workbench
---
Output the data model to Solutions Workbench compatible
        JSON file.

    Parameters
    ----------
    file_path : str
        The location and name of the Solutions Workbench
        JSON file to import.
    write_file : bool, optional
        Whether to write a file, by default True

    Returns
    -------
    SolutionsWorkbenchDataModel
        A representation of the data model in Solutions
        Workbench format.


to_yaml
---
Output the data model to a yaml file and / or yaml
        string.


validate_model
---
Perform additional validation on the data model.

    Parameters
    ----------
    csv_columns : List[str]
        The CSV columns that are allowed in the data model.

    Returns
    -------
    None


visualize
---
Visualize the data model using Graphviz. Requires that
        Graphviz is installed.

    Returns
    -------
    Digraph
        A visual representation of the data model.



## Class Properties


node_dict
---
Returns a dictionary of node label to Node.

    Returns
    -------
    Dict[str, Node]
        A dictionary with node label keys and Node values.


node_labels
---
Returns a list of node labels.

    Returns
    -------
    List[str]
        A list of node labels.


relationship_dict
---
Returns a dictionary of relationship type to
        Relationships.

    Returns
    -------
    Dict[str, Relationship]
        A dictionary with relationship type keys and
        Relationship values.


relationship_types
---
Returns a list of relationship types.

    Returns
    -------
    List[str]
        A list of relationship types.

