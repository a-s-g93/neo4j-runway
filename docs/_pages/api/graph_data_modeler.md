---
permalink: /api/graph-data-modeler/
title: GraphDataModeler
toc: true
toc_label: GraphDataModeler
toc_icon: "fa-solid fa-plane"
---

    from neo4j_runway import GraphDataModeler


 This class is responsible for generating a graph data model
        via communication with an LLM.
 It handles prompt generation, model generation history as
        well as access to the generated data models.

     Attributes
    ----------
    llm : BaseLLM
        The LLM used to generate data models.
    discovery : Union[str, Discovery], optional
        Either a string containing the LLM generated
        discovery or a Discovery object that has been run.
    user_input : Union[Dict[str, str], UserInput], optional
        Either a dictionary with keys general_description
        and column names with descriptions or a UserInput
        object.
    model_iterations : int
        The number of times a data model has been returned.
    model_history : List[DataModel]
        A list of all valid models generated.
    current_model : DataModel
        The most recently generated or loaded data model.



## Class Methods


### __init__
Takes an LLM instance and Discovery information.
    Either a Discovery object can be provided, or each field
        can be provided individually.

    Parameters
    ----------
    llm : BaseLLM
        The LLM used to generate data models.
    discovery : Union[str, Discovery], optional
        Either a string containing the LLM generated
        discovery or a Discovery object that has been run.
        If a Discovery object is provided then the remaining
        discovery attributes don't need to be provided, by
        default ""
    user_input : Union[Dict[str, str], UserInput], optional
        Either a dictionary with keys general_description
        and column names with descriptions or a UserInput
        object, by default dict()
    data_dictionary : Dict[str, Any], optional
        A data dictionary. If single-file input, then the
        keys will be column names and the values are
        descriptions.
        If multi-file input, the keys are file names and
        each contain a nested dictionary of column name keys
        and description values.
        This argument will take precedence over any data
        dictionary provided via the Discovery object.
        This argument will take precedence over the
        allowed_columns argument. By default None
    allowed_columns : List[str], optional
        A list of allowed columns for modeling. Can be used
        only for single-file inputs. By default = list()


### create_initial_model
Generate the initial model.
    You may access this model with the `get_model` method
        and providing `version=1`.

    Parameters
    ----------
    max_retries : int, optional
        The max number of retries for generating the initial
        model, by default 3
    use_yaml_data_model : bool, optional
        Whether to pass the data model in YAML format while
        making corrections, by default False
    use_advanced_data_model_generation_rules, optional
        Whether to include advanced data modeling rules, by
        default True
    allow_duplicate_properties : bool, optional
        Whether to allow a property to exist on multiple
        node labels or relationship types, by default False
    enforce_uniqueness : bool, optional
        Whether to error if a node has no unique identifiers
        (unique or node key).
        Setting this to false may be detrimental during code
        generation and ingestion. By default True

    Returns
    -------
    Union[DataModel, str]
        The generated data model if a valid model is
        generated, or
        A dictionary containing information about the failed
        generation attempt.


### get_model
Get the data model version specified.
    By default will return the most recent model.
    Version are 1-indexed.

    Parameters
    ----------
    version : int, optional
        The model version, 1-indexed, by default -1
    as_dict : bool, optional
        whether to return as a Python dictionary. Will
        otherwise return a DataModel object, by default
        False

    Returns
    -------
    Union[DataModel, Dict[str, Any]]
        The data model in desired format.

    Examples
    --------
    >>> gdm.get_model(1) == gdm.model_history[0]
    True


### iterate_model
Iterate on the current model. A data model must exist in
        the `model_history` property to run.

    Parameters
    ----------
    iterations : int, optional
        How many times to perform model generation. Each
        successful iteration will be appended to the
        GraphDataModeler model_history.
        For example if a value of 2 is provided, then two
        successful models will be appended to the
        model_history. Model generation will use the same
        prompt for each generation attempt. By default 1
    corrections : Union[str, None], optional
        What changes the user would like the LLM to address
        in the next model, by default None
    max_retries : int, optional
        The max number of retries for generating the initial
        model, by default 3
    use_yaml_data_model : bool, optional
        Whether to pass the data model in YAML format while
        making corrections, by default False
    use_advanced_data_model_generation_rules, optional
        Whether to include advanced data modeling rules, by
        default True
    allow_duplicate_properties : bool, optional
        Whether to allow a property to exist on multiple
        node labels or relationship types, by default False
    enforce_uniqueness : bool, optional
        Whether to error if a node has no unique identifiers
        (unique or node key).
        Setting this to false may be detrimental during code
        generation and ingestion. By default True

    Returns
    -------
    DataModel
        The most recent generated data model.


### load_model
Append a new data model to the end of the
        `model_history`.
    This will become the new `current_model`.

    Parameters
    ----------
    data_model : DataModel
        The new data model.

    Raises
    ------
    ValueError
        If the data_model is not an instance of DataModel.



## Class Properties


### allowed_columns
The allowed columns for model generation.
    If multi-file, then a dictionary with file name keys and
        list of columns for values.
    If single-file, then a list of columns.

    Returns
    -------
    Dict[str, List[str]]
        The allowd columns for data model generation.

    Raises
    ------
    AssertionError
        When no _data_dictionary attribute is initialized in
        the GraphDataModeler class.


### current_model
Get the most recently created or loaded data model.

    Returns
    -------
    DataModel
        The current data model.


### current_model_viz
Visualize the most recent model with Graphviz.

    Returns
    -------
    Digraph
        The object to visualize.


### is_multifile
Whether data is multi-file or not.

    Returns
    -------
    bool
        True if multi-file detected, else False
