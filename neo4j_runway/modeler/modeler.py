from typing import Any, Dict, List, Optional, Union
import warnings

from graphviz import Digraph

from ..discovery import Discovery
from ..inputs import UserInput
from ..llm import LLM
from ..models import DataModel
from ..resources.prompts import (
    create_initial_data_model_prompt,
    create_data_model_iteration_prompt,
)


class GraphDataModeler:
    """
    This class is responsible for generating a graph data model via communication with an LLM.
    It handles prompt generation, model generation history as well as access to the generated data models.
    """

    def __init__(
        self,
        llm: LLM,
        discovery: Union[str, Discovery] = "",
        user_input: Union[Dict[str, str], UserInput] = dict(),
        general_data_description: str = "",
        numeric_data_description: str = "",
        categorical_data_description: str = "",
        feature_descriptions: str = "",
        allowed_columns: List[str] = list(),
    ) -> None:
        """
        Takes an LLM instance and Discovery information.
        Either a Discovery object can be provided, or each field can be provided individually.

        Attributes
        ----------
        llm : LLM
            The LLM used to generate data models.
        discovery : Union[str, Discovery], optional
            Either a string containing the LLM generated discovery or a Discovery object that has been run.
            If a Discovery object is provided then the remaining discovery attributes don't need to be provided, by default ""
        user_input : Union[Dict[str, str], UserInput], optional
            Either a dictionary with keys general_description and column names with descriptions or a UserInput object, by default {}
        general_data_description : str, optional
            A general data description provided by Pandas, by default ""
        numeric_data_description : str, optional
            A numeric data description provided by Pandas, by default ""
        categorical_data_description : str, optional
            A categorical data description provided by Pandas, by default ""
        feature_descriptions : str, optional
            Feature (column) descriptions provided by Discovery, by default ""
        allowed_columns : List[str], optional
            The columns that may be used in the data model. The argument should only be used in no columns are specified in
            the discovery or user_input arguments. By default []
        """

        self.llm = llm

        if isinstance(discovery, Discovery):
            self.user_input = discovery.user_input

            self.columns_of_interest = discovery.columns_of_interest

            self.discovery = discovery.discovery
            self.general_info = discovery.df_info
            self.description_numeric = discovery.numeric_data_description
            self.description_categorical = discovery.categorical_data_description
            self.feature_descriptions = discovery.user_input.column_descriptions

        else:

            # we convert all user_input to a UserInput object
            if not isinstance(user_input, UserInput):
                general_description = (
                    user_input["general_description"]
                    if "general_description" in user_input
                    else ""
                )
                if "general_description" in user_input.keys():
                    del user_input["general_description"]
                else:
                    warnings.warn(
                        "user_input should include key:value pair {general_description: ...} for best results. "
                    )
                self.user_input = UserInput(
                    general_description=general_description,
                    column_descriptions=user_input,
                )
            else:
                self.user_input = user_input

            self.columns_of_interest = (
                allowed_columns or self.user_input.allowed_columns
            )

            self.discovery = discovery
            self.general_info = general_data_description
            self.description_numeric = numeric_data_description
            self.description_categorical = categorical_data_description
            self.feature_descriptions = feature_descriptions

        if self.discovery == "":
            warnings.warn(
                "It is highly recommended to provide discovery generated from the Discovery module."
            )

        self._initial_model_created: bool = False
        self.model_iterations: int = 0
        self.model_history: List[DataModel] = []

    @property
    def current_model(self) -> DataModel:
        """
        Get the most recently created or loaded data model.

        Returns
        -------
        DataModel
            The current data model.
        """

        assert len(self.model_history) > 0, "No models found in history."

        return self.model_history[-1]

    @property
    def current_model_viz(self) -> Digraph:
        """
        Visualize the most recent model with Graphviz.

        Returns
        -------
        Digraph
            The object to visualize.
        """

        assert len(self.model_history) > 0, "No models found in history."

        return self.current_model.visualize()

    def load_model(self, data_model: DataModel) -> None:
        """
        Append a new data model to the end of the `model_history`.
        This will become the new `current_model`.

        Parameters
        ----------
        data_model : DataModel
            The new data model.

        Raises
        ------
        ValueError
            If the data_model is not an instance of DataModel.
        """

        if not isinstance(data_model, DataModel):
            raise ValueError("Provided data model is not of type <DataModel>!")

        self.model_history.append(data_model)
        self._initial_model_created = True

    def get_model(
        self, version: int = -1, as_dict: bool = False
    ) -> Union[DataModel, Dict[str, Any]]:
        """
        Get the data model version specified.
        By default will return the most recent model.
        Version are 1-indexed.

        Parameters
        ----------
        version : int, optional
            The model version, 1-indexed, by default -1
        as_dict : bool, optional
            whether to return as a Python dictionary. Will otherwise return a DataModel object, by default False

        Returns
        -------
        Union[DataModel, Dict[str, Any]]
            The data model in desired format.

        Examples
        --------
        >>> gdm.get_model(1) == gdm.model_history[0]
        True
        """

        assert len(self.model_history) > 0, "No models found in history."
        assert version != 0, "No model version 0."
        if version < 0:
            assert version + len(self.model_history) >= 0, "Model version out of range."
        else:
            assert len(self.model_history) - version >= 0, "Model version out of range."
            # adjust for index
            version -= 1

        return (
            self.model_history[version].model_dump()
            if as_dict
            else self.model_history[version]
        )

    def create_initial_model(self) -> DataModel:
        """
        Generate the initial model. This must be ran before a model can be interated on.
        You may access this model with the `get_model` method and providing `version=1`.

        Returns
        -------
        DataModel
            The generated data model.
        """

        response = self.llm._get_data_model_response(
            formatted_prompt=create_initial_data_model_prompt(
                discovery_text=self.discovery,
                user_input=self.user_input,
                pandas_general_info=self.general_info,
                feature_descriptions=self.feature_descriptions,
            ),
            csv_columns=self.columns_of_interest,
        )

        self.model_history.append(response)

        self._initial_model_created = True

        return response

    def iterate_model(
        self,
        iterations: int = 1,
        user_corrections: Optional[str] = None,
        use_yaml_data_model: bool = False,
    ) -> str:
        """
        Iterate on the current model. A data model must exist in the `model_history` property to run.

        Parameters
        ----------
        iterations : int, optional
            How many times to perform model generation. Each successful iteration will be appended to the GraphDataModeler model_history.
            For example if a value of 2 is provided, then two successful models will be appended to the model_history. Model generation will use the same
            prompt for each generation attempt. By default 1
        user_corrections : Union[str, None], optional
            What changes the user would like the LLM to address in the next model, by default None
        use_yaml_data_model : bool, optional
            Whether to pass the data model in yaml format to the generation prompt.
            This takes less tokens, but differs from the output format of json. By default False

        Returns
        -------
        DataModel
            The most recent generated data model.
        """

        assert self._initial_model_created, "No data model present to iterate on."

        def iterate() -> DataModel:
            for _ in range(0, iterations):
                response = self.llm._get_data_model_response(
                    formatted_prompt=create_data_model_iteration_prompt(
                        discovery_text=self.discovery,
                        user_input=self.user_input,
                        pandas_general_info=self.general_info,
                        feature_descriptions=self.feature_descriptions,
                        data_model_to_modify=self.current_model,
                        user_corrections=user_corrections,
                        use_yaml_data_model=use_yaml_data_model,
                    ),
                    csv_columns=self.columns_of_interest,
                    use_yaml_data_model=use_yaml_data_model,
                )

                self.model_history.append(response)
                self.model_iterations += 1

            return response

        current_model = iterate()

        return current_model
