---
permalink: /api/discovery/
---
# Discovery


## Class Methods


__init__
---
The Discovery module that handles summarization and
        discovery generation via an LLM.

    Parameters
    ----------
    llm : LLM, optional
        The LLM instance used to generate data discovery.
        Only required if pandas_only = False.
    user_input : Union[Dict[str, str], UserInput]
        User provided descriptions of the data.
        If a dictionary, then should contain the keys
        "general_description" and all desired columns., by
        default = {}
    data : pd.DataFrame
        The data in Pandas DataFrame format.
    pandas_only : bool
        Whether to only generate discovery using Pandas.
        Will not call the LLM service.


run
---
Run the discovery process on the provided DataFrame.
    Access generated discovery with the .view_discovery()
        method of the Discovery class.

    Returns
    -------
    show_result: bool
        Whether to print the generated discovery upon
        retrieval.
    notebook: bool
        Whether code is executed in a notebook. Affects the
        result print formatting.


to_markdown
---
Save the generated discovery to a .md file.


to_txt
---
Save the generated discovery to a .txt file.


view_discovery
---
Print the discovery information.

    Parameters
    ----------
    notebook : bool, optional
        Whether executing in a notebook, by default True

