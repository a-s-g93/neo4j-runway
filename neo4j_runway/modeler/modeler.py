import warnings
from typing import Any, Dict, List, Optional, Union

from graphviz import Digraph

from ..discovery import Discovery
from ..inputs import UserInput, user_input_safe_construct
from ..llm.base import BaseDataModelingLLM
from ..models import DataModel
from ..resources.prompts.data_modeling import (
    create_data_model_iteration_prompt,
)
from ..warnings import ExperimentalFeatureWarning


class GraphDataModeler:
    """
    This class is responsible for generating a graph data model via communication with an LLM.
    It handles prompt generation, model generation history as well as access to the generated data models.

     Attributes
    ----------
    llm : BaseLLM
        The LLM used to generate data models.
    discovery : Union[str, Discovery], optional
        Either a string containing the LLM generated discovery or a Discovery object that has been run.
    user_input : Union[Dict[str, str], UserInput], optional
        Either a dictionary with keys general_description and column names with descriptions or a UserInput object.
    model_iterations : int
        The number of times a data model has been returned.
    model_history : List[DataModel]
        A list of all valid models generated.
    current_model : DataModel
        The most recently generated or loaded data model.
    """

    def __init__(
        self,
        llm: BaseDataModelingLLM,
        discovery: Union[str, Discovery] = "",
        user_input: Union[Dict[str, str], UserInput] = dict(),
        data_dictionary: Optional[Dict[str, Any]] = None,
        allowed_columns: List[str] = list(),
    ) -> None:
        """
        Takes an LLM instance and Discovery information.
        Either a Discovery object can be provided, or each field can be provided individually.

        Parameters
        ----------
        llm : BaseLLM
            The LLM used to generate data models.
        discovery : Union[str, Discovery], optional
            Either a string containing the LLM generated discovery or a Discovery object that has been run.
            If a Discovery object is provided then the remaining discovery attributes don't need to be provided, by default ""
        user_input : Union[Dict[str, str], UserInput], optional
            Either a dictionary with keys general_description and column names with descriptions or a UserInput object, by default dict()
        data_dictionary : Dict[str, Any], optional
            A data dictionary. If single-file input, then the keys will be column names and the values are descriptions.
            If multi-file input, the keys are file names and each contain a nested dictionary of column name keys and description values.
            This argument will take precedence over any data dictionary provided via the Discovery object.
            This argument will take precedence over the allowed_columns argument. By default None
        allowed_columns : List[str], optional
            A list of allowed columns for modeling. Can be used only for single-file inputs. By default = list()
        """

        self.llm = llm

        if isinstance(discovery, Discovery):
            self.user_input = discovery.user_input
            # data dictionary should have been constructed before / during the discovery phase
            self._data_dictionary = discovery.data.data_dictionary

            self.discovery = discovery.discovery

        else:
            if not allowed_columns and not user_input and not data_dictionary:
                raise ValueError(
                    "Not enough information provided. Please provide a Discovery object, user_input, allowed_columns or a data_dictionary respectively to the constructor."
                )
            # we convert all user_input to a UserInput object
            elif not isinstance(user_input, UserInput):
                self.user_input = user_input_safe_construct(
                    unsafe_user_input=user_input,
                    allowed_columns=allowed_columns,
                    data_dictionary=data_dictionary,
                )
            else:
                self.user_input = user_input

            self.discovery = discovery

        # set the data dictionary
        # we take the data_dictionary arg first in cases where
        # a user may want to slightly modify the features available for modeling,
        # but still use the generated discovery information
        if data_dictionary is not None:
            self._data_dictionary = data_dictionary

        else:
            # this is a data dictionary derived from the allowed_columns arg
            # or the original user_input
            self._data_dictionary = self.user_input.data_dictionary

        if self.discovery == "":
            warnings.warn(
                "It is highly recommended to provide discovery generated from the Discovery module."
            )

        self._initial_model_created: bool = False
        self.model_iterations: int = 0
        self.model_history: List[DataModel] = list()

        if self.is_multifile:
            warnings.warn(
                message="Multi file Data Modeling is an experimental feature and may not work as expected. Please use with caution and raise any issues encountered here: https://github.com/a-s-g93/neo4j-runway/issues",
                category=ExperimentalFeatureWarning,
            )

    @property
    def is_multifile(self) -> bool:
        """
        Whether data is multi-file or not.

        Returns
        -------
        bool
            True if multi-file detected, else False
        """
        if isinstance(self.discovery, Discovery):
            return self.discovery.data.size > 1

        if (
            len(list(self._data_dictionary.keys())) == 1
        ):  # assumes always more than 1 column for modeling
            return False

        return self.user_input.is_multifile

    @property
    def allowed_columns(self) -> Dict[str, List[str]]:
        """
        The allowed columns for model generation.
        If multi-file, then a dictionary with file name keys and list of columns for values.
        If single-file, then a list of columns.

        Returns
        -------
        Dict[str, List[str]]
            The allowd columns for data model generation.

        Raises
        ------
        AssertionError
            When no _data_dictionary attribute is initialized in the GraphDataModeler class.
        """

        assert (
            self._data_dictionary is not None
        ), "No data dictionary present in GraphDataModeler class."

        if self.is_multifile:
            return {
                k: [col for col, desc in v.items() if not desc.endswith("ignore")]
                for k, v in self._data_dictionary.items()
            }
        else:
            return {
                "file": [
                    col
                    for col, desc in self._data_dictionary.items()
                    if not desc.endswith("ignore")
                ]
            }

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

    def create_initial_model(
        self,
        max_retries: int = 3,
        use_yaml_data_model: bool = False,
        use_advanced_data_model_generation_rules: bool = True,
        allow_duplicate_properties: bool = False,
        enforce_uniqueness: bool = True,
    ) -> Union[DataModel, Dict[str, Any]]:
        """
        Generate the initial model.
        You may access this model with the `get_model` method and providing `version=1`.

        Parameters
        ----------
        max_retries : int, optional
            The max number of retries for generating the initial model, by default 3
        use_yaml_data_model : bool, optional
            Whether to pass the data model in YAML format while making corrections, by default False
        use_advanced_data_model_generation_rules, optional
            Whether to include advanced data modeling rules, by default True
        allow_duplicate_properties : bool, optional
            Whether to allow a property to exist on multiple node labels or relationship types, by default False
        enforce_uniqueness : bool, optional
            Whether to error if a node has no unique identifiers (unique or node key).
            Setting this to false may be detrimental during code generation and ingestion. By default True

        Returns
        -------
        Union[DataModel, str]
            The generated data model if a valid model is generated, or
            A dictionary containing information about the failed generation attempt.
        """

        response = self.llm._get_initial_data_model_response(
            discovery_text=self.discovery,
            valid_columns=self.allowed_columns,
            data_dictionary=self._data_dictionary,
            use_cases=self.user_input.pretty_use_cases,
            multifile=self.is_multifile,
            use_advanced_data_model_generation_rules=use_advanced_data_model_generation_rules,
            max_retries=max_retries,
            use_yaml_data_model=use_yaml_data_model,
            allow_duplicate_properties=allow_duplicate_properties,
            enforce_uniqueness=enforce_uniqueness,
        )

        if isinstance(response, dict):
            return response

        self.model_history.append(response)

        self._initial_model_created = True

        return response

    def iterate_model(
        self,
        iterations: int = 1,
        corrections: Optional[str] = None,
        use_advanced_data_model_generation_rules: bool = True,
        use_yaml_data_model: bool = False,
        max_retries: int = 3,
        allow_duplicate_properties: bool = False,
        enforce_uniqueness: bool = True,
    ) -> DataModel:
        """
        Iterate on the current model. A data model must exist in the `model_history` property to run.

        Parameters
        ----------
        iterations : int, optional
            How many times to perform model generation. Each successful iteration will be appended to the GraphDataModeler model_history.
            For example if a value of 2 is provided, then two successful models will be appended to the model_history. Model generation will use the same
            prompt for each generation attempt. By default 1
        corrections : Union[str, None], optional
            What changes the user would like the LLM to address in the next model, by default None
        max_retries : int, optional
            The max number of retries for generating the initial model, by default 3
        use_yaml_data_model : bool, optional
            Whether to pass the data model in YAML format while making corrections, by default False
        use_advanced_data_model_generation_rules, optional
            Whether to include advanced data modeling rules, by default True
        allow_duplicate_properties : bool, optional
            Whether to allow a property to exist on multiple node labels or relationship types, by default False
        enforce_uniqueness : bool, optional
            Whether to error if a node has no unique identifiers (unique or node key).
            Setting this to false may be detrimental during code generation and ingestion. By default True

        Returns
        -------
        DataModel
            The most recent generated data model.
        """

        assert self._initial_model_created, "No data model present to iterate on."

        def iterate() -> DataModel:
            for _ in range(0, iterations):
                formatted_prompt = create_data_model_iteration_prompt(
                    discovery_text=self.discovery,
                    data_model_to_modify=self.current_model,
                    multifile=self.is_multifile,
                    corrections=corrections,
                    data_dictionary=self._data_dictionary,
                    use_cases=self.user_input.pretty_use_cases,
                    use_yaml_data_model=use_yaml_data_model,
                    advanced_rules=use_advanced_data_model_generation_rules,
                    valid_columns=self.allowed_columns,
                )
                response = self.llm._get_data_model_response(
                    formatted_prompt=formatted_prompt,
                    max_retries=max_retries,
                    valid_columns=self.allowed_columns,
                    use_yaml_data_model=use_yaml_data_model,
                    data_dictionary=self._data_dictionary,
                    allow_duplicate_properties=allow_duplicate_properties,
                    enforce_uniqueness=enforce_uniqueness,
                )

                self.model_history.append(response)
                self.model_iterations += 1

            return response

        current_model = iterate()

        return current_model
