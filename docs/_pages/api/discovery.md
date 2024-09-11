---
permalink: /api/discovery/
title: Discovery
toc: true
toc_label: Discovery
toc_icon: "fa-solid fa-plane"
---

    from neo4j_runway import Discovery


 The Discovery module that handles summarization and
        discovery generation via Pandas and an optional LLM.

    Attributes
    ----------
    llm : BaseDiscoveryLLM
        The LLM instance used to generate data discovery.
    user_input : UserInput
        User provided descriptions of the data.
        A class containing user provided information about
        the data.
    data : TableCollection
        The data contained in a TableCollection.
        All data provided to the Discovery constructor is
        converted to a Table and placed in a TableCollection
        class.



## Class Methods


### __init__
The Discovery module that handles summarization and
        discovery generation via Pandas and an optional LLM.

    Parameters
    ----------
    data : Union[pd.DataFrame, Table, TableCollection]
        The data to run discovery on. Can be either a Pandas
        DataFrame, Runway Table or Runway TableCollection.
        Multi file inputs should be provided via the
        TableCollection class.
        Single file inputs may be provided as a DataFrame or
        Runway Table. They will be placed in a
        TableCollection class upon initialization of the
        Discovery class.
    llm : LLM, optional
        The LLM instance used to generate data discovery.
        If running discovery for multiple files,
        it is recommended to use an async compatible LLM and
        use the `run_async` method.
        Not required if only interested in generating Pandas
        summaries. By default None.
    user_input : Union[Dict[str, str], UserInput]
        User provided descriptions of the data.
        If a dictionary, then should contain the keys
        "general_description" and all desired columns.
        This is only necessary if providing a Pandas
        DataFrame as data input. Otherwise it will be
        ignored. By default = dict()


### run
Run the discovery process on the provided data.
    This method is compatible with non-async LLM classes. If
        using an async LLM, please use the `run_async`
        method instead.
    Access generated discovery with the .view_discovery()
        method of the Discovery class.

    If running multi-file discovery, the parameter priority
        is as follows:
    1. custom_batches
    2. bulk_process
    3. num_calls
    4. batch_size

    If more than one of the above is provided, the highest
        priority will overwrite any others.

    Parameters
    ----------
    show_result : bool, optional
        Whether to print the final generated discovery upon
        retrieval. By default True
    notebook : bool, optional
        Whether code is executed in a notebook. Affects the
        result print formatting. By default True
    ignore_files : List[str], optional
        A list of files to ignore. For multi-file input. By
        default list()
    batch_size : int, optional
        The number of files to include in a discovery call.
        For multi-file input. By default 1
    bulk_process : bool, optional
        Whether to include all files in a single batch. For
        multi-file input. By default False
    num_calls : Optional[int], optional
        The max number of LLM calls to make during the
        discovery process. For multi-file input. By default
        None
    custom_batches : Optional[List[List[str]]], optional
        A list of custom batches to run discovery on. For
        multi-file input. By default None
    pandas_only : bool, optional
        Whether to only run Pandas summary generation and
        skip LLM calls. By default False

    Raises
    ------
    RuntimeError
        If an async LLM is provided to the Discovery
        constructor.
    PandasDataSummariesNotGeneratedError
        If Pandas summaries are unable to be generated.


### run_async
Run the discovery process on the provided data
        asynchronously.
    This method is compatible with async LLM classes. If
        using a non async LLM, please use the `run` method
        instead.
    Access generated discovery with the .view_discovery()
        method of the Discovery class.

    If running multi-file discovery, the parameter priority
        is as follows:
    1. custom_batches
    2. bulk_process
    3. num_calls
    4. batch_size

    If more than one of the above is provided, the highest
        priority will overwrite any others.

    Parameters
    ----------
    show_result : bool, optional
        Whether to print the final generated discovery upon
        retrieval. By default True
    notebook : bool, optional
        Whether code is executed in a notebook. Affects the
        result print formatting. By default True
    ignore_files : List[str], optional
        A list of files to ignore. For multi-file input. By
        default list()
    batch_size : int, optional
        The number of files to include in a discovery call.
        For multi-file input. By default 1
    bulk_process : bool, optional
        Whether to include all files in a single batch. For
        multi-file input. By default False
    num_calls : Optional[int], optional
        The max number of LLM calls to make during the
        discovery process. For multi-file input. By default
        None
    custom_batches : Optional[List[List[str]]], optional
        A list of custom batches to run discovery on. For
        multi-file input. By default None

    Raises
    ------
    RuntimeError
        If a non async LLM is provided to the Discovery
        constructor.


### to_markdown
Output findings to a .md file.

    Parameters
    ----------
    file_dir : str, optional
        The directory to save files to, by default "./"
    file_name : str, optional
        'all' to export all data, 'final' to export only
        final discovery result, file name to export the
        desired file only, by default "all"
    include_pandas : bool, optional
        Whether to include the Pandas summaries, by default
        True


### to_txt
Output findings to a .txt file.

    Parameters
    ----------
    file_dir : str, optional
        The directory to save files to, by default "./"
    file_name : str, optional
        'all' to export all data, 'final' to export only
        final discovery result, file name to export the
        desired file only, by default "all"
    include_pandas : bool, optional
        Whether to include the Pandas summaries, by default
        True


### view_discovery
Print the discovery information of the provided file.
    If no file_name is provided, then displays the
        summarized final discovery.

    Parameters
    ----------
    file_name : str, optional
        The file to display discovery. If not provided, then
        displays the summarized final discovery. By default
        = None
    notebook : bool, optional
        Whether executing in a notebook, by default True



## Class Properties


### discovery
The final generated discovery for the data.

    Returns
    -------
    str
        The `discovery` attribute of the `data` attribute.


### is_multifile
Whether data is multi-file or not.

    Returns
    -------
    bool
        True if multi-file detected, else False
