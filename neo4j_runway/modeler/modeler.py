import warnings
from typing import Any, Dict, List, Optional, Union

from graphviz import Digraph

from ..discovery import Discovery
from ..inputs import UserInput
from ..llm.base import BaseDataModelingLLM
from ..models import DataModel
from ..resources.prompts.data_modeling import (
    create_data_model_iteration_prompt,
)
from ..utils.data.data_dictionary.data_dictionary import DataDictionary
from ..utils.data.data_dictionary.utils import (
    load_data_dictionary_from_compact_python_dictionary,
)
from ..warnings import ExperimentalFeatureWarning


class GraphDataModeler:
    """
    Handles generating a graph data model via communication with an LLM.
    It handles prompt generation, model generation history as well as access to the generated data models.

    """

    def __init__(
        self,
        llm: BaseDataModelingLLM,
        discovery: Union[str, Discovery] = "",
        user_input: Optional[Union[Dict[str, str], UserInput]] = None,
        data_dictionary: Optional[DataDictionary] = None,
        use_cases: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Takes an LLM instance and Discovery information.
        NOTE: It is highly recommended to provide the Discovery object directly to the constructor.

        Parameters
        ----------
        llm : BaseLLM
            The LLM used to generate data models.
        discovery : Union[str, Discovery], optional
            Either a string containing the LLM generated discovery or a Discovery object that has been run.
            If a Discovery object is provided then the remaining discovery attributes don't need to be provided, by default ""
        user_input : Union[Dict[str, str], UserInput], optional
            Either a dictionary with keys general_description and column names with descriptions or a UserInput object, by default None
            .. deprecated:: 0.15.0
                `user_input` will be removed as its functions are handled better by `TableCollection` and `DataDictionary`.
        data_dictionary : Optional[DataDictionary], optional
            A `DataDictionary` object describing the data
            This argument will take precedence over any data dictionary provided via the Discovery object. By default None
        """

        self.llm = llm
        self.use_cases = (
            use_cases  # will be overwritten if a Discovery object is provided
        )

        # we prefer users to provide the Discovery object
        if isinstance(discovery, Discovery):
            # data dictionary should have been constructed before / during the discovery phase
            self.data_dictionary = discovery.data.data_dictionary
            self.discovery = discovery.discovery

        # if no Discovery object is provided, they should have a proper DataDictionary object
        elif data_dictionary is not None:
            self.data_dictionary = data_dictionary
            self.discovery = discovery

        # as a last resort we can parse any `user_input` values they pass. This will be phased out in later versions.
        elif isinstance(user_input, dict):
            user_input.pop("general_description", None)
            self.data_dictionary = load_data_dictionary_from_compact_python_dictionary(
                user_input
            )
            self.discovery = discovery
        elif isinstance(user_input, UserInput):
            if isinstance(user_input.data_dictionary, DataDictionary):
                self.data_dictionary = user_input.data_dictionary
            else:
                self.data_dictionary = (
                    load_data_dictionary_from_compact_python_dictionary(
                        user_input.data_dictionary
                    )
                )
            self.discovery = discovery
            self.use_cases = user_input.use_cases or use_cases

        # otherwise crash
        else:
            raise ValueError(
                "Not enough information provided. Please provide a Discovery object or a valid data_dictionary to the constructor."
            )

        if not self.discovery:
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

        return self.data_dictionary.is_multifile

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
        """

        return self.data_dictionary.table_column_names_dict

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
        use_advanced_data_model_generation_rules: bool = True,
        allow_duplicate_properties: bool = False,
        enforce_uniqueness: bool = True,
        allow_parallel_relationships: bool = False,
        apply_neo4j_naming_conventions: bool = True,
        **kwargs: Any,
    ) -> DataModel:
        """
        Generate the initial model.
        You may access this model with the `get_model` method and providing `version=1`.

        Parameters
        ----------
        max_retries : int, optional
            The max number of retries for generating the initial model, by default 3
        use_advanced_data_model_generation_rules, optional
            Whether to include advanced data modeling rules, by default True
        allow_duplicate_properties : bool, optional
            Whether to allow a property to exist on multiple node labels or relationship types, by default False
        enforce_uniqueness : bool, optional
            Whether to error if a node has no unique identifiers (unique or node key).
            Setting this to false may be detrimental during code generation and ingestion. By default True
        allow_parallel_relationships : bool, optional
            Whether to allow parallel relationships to exist in the data model, by default False
        apply_neo4j_naming_conventions : bool, optional
            Whether to apply Neo4j naming conventions to the generated Data Model, by default True

        Returns
        -------
        DataModel
            The generated data model.
        """

        response = self.llm._get_initial_data_model_response(
            discovery_text=self.discovery,
            valid_columns=self.allowed_columns,
            data_dictionary=self.data_dictionary,
            use_cases=self.use_cases,
            multifile=self.is_multifile,
            use_advanced_data_model_generation_rules=use_advanced_data_model_generation_rules,
            max_retries=max_retries,
            allow_duplicate_properties=allow_duplicate_properties,
            enforce_uniqueness=enforce_uniqueness,
            allow_parallel_relationships=allow_parallel_relationships,
            apply_neo4j_naming_conventions=apply_neo4j_naming_conventions,
        )

        self.model_history.append(response)

        self._initial_model_created = True

        return response

    def iterate_model(
        self,
        iterations: int = 1,
        corrections: Optional[str] = None,
        use_advanced_data_model_generation_rules: bool = True,
        max_retries: int = 3,
        allow_duplicate_properties: bool = False,
        enforce_uniqueness: bool = True,
        allow_parallel_relationships: bool = False,
        apply_neo4j_naming_conventions: bool = True,
        **kwargs: Any,
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
        use_advanced_data_model_generation_rules, optional
            Whether to include advanced data modeling rules, by default True
        allow_duplicate_properties : bool, optional
            Whether to allow a property to exist on multiple node labels or relationship types, by default False
        enforce_uniqueness : bool, optional
            Whether to error if a node has no unique identifiers (unique or node key).
            Setting this to false may be detrimental during code generation and ingestion. By default True
        allow_parallel_relationships : bool, optional
            Whether to allow parallel relationships to exist in the data model, by default False
        apply_neo4j_naming_conventions : bool, optional
            Whether to apply Neo4j naming conventions to the generated Data Model, by default True

        Returns
        -------
        DataModel
            The most recently generated data model.
        """

        if "user_corrections" in kwargs:
            corrections = kwargs["user_corrections"]

        assert self._initial_model_created, "No data model present to iterate on."

        def iterate() -> DataModel:
            for _ in range(0, iterations):
                formatted_prompt = create_data_model_iteration_prompt(
                    discovery_text=self.discovery,
                    data_model_to_modify=self.current_model,
                    multifile=self.is_multifile,
                    corrections=corrections,
                    data_dictionary=self.data_dictionary,
                    use_cases=self.use_cases,
                    advanced_rules=use_advanced_data_model_generation_rules,
                    valid_columns=self.allowed_columns,
                )
                response = self.llm._get_data_model_response(
                    formatted_prompt=formatted_prompt,
                    max_retries=max_retries,
                    valid_columns=self.allowed_columns,
                    data_dictionary=self.data_dictionary,
                    allow_duplicate_properties=allow_duplicate_properties,
                    enforce_uniqueness=enforce_uniqueness,
                    allow_parallel_relationships=allow_parallel_relationships,
                    apply_neo4j_naming_conventions=apply_neo4j_naming_conventions,
                )

                self.model_history.append(response)
                self.model_iterations += 1

            return response

        current_model = iterate()

        return current_model
