---
permalink: /api/graph-data-modeler/
---
# GraphDataModeler


## Class Methods


__init__
---
Takes an LLM instance and Discovery information.
    Either a Discovery object can be provided, or each field
        can be provided individually.

    Parameters
    ----------
    llm : LLM
        The LLM used to generate data models.
    discovery : Union[str, Discovery], optional
        Either a string containing the LLM generated
        discovery or a Discovery object that has been ran.
        If a Discovery object is provided then the remaining
        discovery attributes don't need to be provided, by
        default ""
    user_input : Dict[str, UserInput], optional
        Either a dictionary with keys general_description
        and column names with descriptions or a UserInput
        object, by default {}
    general_data_description : str, optional
        A general data description provided by Discovery, by
        default ""
    numeric_data_description : str, optional
        A numeric data description provided by Discovery, by
        default ""
    categorical_data_description : str, optional
        A categorical data description provided by
        Discovery, by default ""
    feature_descriptions : str, optional
        Feature descriptions provided by Discovery, by
        default ""
    allowed_columns : List[str], optional
        The columns that may be used in the data model. The
        argument should only be used in no columns are
        specified in
        the discovery or user_input arguments., by default
        []


create_initial_model
---
Create the initial model.


get_model
---
Returns the data model version specified. Example:
        Version 1 will return model_history index 0.
    By default will return the most recent model.
    Allows access to the intial model.


iterate_model
---
Iterate on the previous data model the number times
        indicated.


load_model
---
Append a new data model to the end of the model_history.
    This will become the new current_model.



## Class Properties


__dict__
---



current_model
---
The current data model.


current_model_viz
---
The current data model visualized with Graphviz.

