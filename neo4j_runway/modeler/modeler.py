from typing import Dict, Any, Union
import warnings

from graphviz import Digraph

from ..discovery import Discovery
from ..llm import LLM
from ..objects import DataModel
from ..resources.prompts.prompts import model_generation_rules, model_format


class GraphDataModeler:

    def __init__(
        self,
        llm: LLM,
        discovery: Union[str, Discovery] = "",
        user_input: Dict[str, str] = {},
        general_data_description: str = "",
        numeric_data_description: str = "",
        categorical_data_description: str = "",
        feature_descriptions: str = "",
    ) -> None:
        """
        Takes an LLM instance and Discovery information. Either a Discovery object can be provided, or each field can be provided individually.
        """

        self.llm = llm

        if isinstance(discovery, Discovery):
            # print("discovery instance")
            self.user_input = discovery.user_input

            assert "general_description" in self.user_input.keys(), (
                "user_input must include key:value pair {general_description: ...}. "
                + f"Found keys {self.user_input.keys()}"
            )

            self.columns_of_interest = discovery.columns_of_interest

            self.discovery = discovery.discovery
            self.general_info = discovery.df_info
            self.description_numeric = discovery.numeric_data_description
            self.description_categorical = discovery.categorical_data_description
            self.feature_descriptions = discovery.feature_descriptions

        else:
            # print("no discovery instance")
            self.user_input = user_input

            assert "general_description" in self.user_input.keys(), (
                "user_input must include key:value pair {general_description: ...}. "
                + f"Found keys {self.user_input.keys()}"
            )

            self.columns_of_interest = list(user_input.keys())
            self.columns_of_interest.remove("general_description")

            self.discovery = discovery
            self.general_info = general_data_description
            self.description_numeric = numeric_data_description
            self.description_categorical = categorical_data_description
            self.feature_descriptions = feature_descriptions

        if self.discovery == "":
            warnings.warn(
                "It is highly recommended to provide discovery generated from the Discovery module."
            )

        self._initial_model_created = False
        self.model_iterations = 0
        self.model_history = []

    @property
    def current_model(self) -> DataModel:
        """
        The current data model.
        """

        assert len(self.model_history) > 0, "No models found in history."

        return self.model_history[-1]

    def get_model(
        self, version: int = -1, as_dict: bool = False
    ) -> Union[DataModel, Dict[str, Any]]:
        """
        Returns the data model version specified.
        By default will return the most recent model.
        Allows access to the intial model.
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

    @property
    def current_model_viz(self) -> Digraph:
        """
        The current data model visualized with Graphviz.
        """

        assert len(self.model_history) > 0, "No models found in history."

        return self.current_model.visualize()

    def _generate_initial_data_model_prompt(self) -> str:
        """
        Generate the initial data model request prompt.
        """
        prompt = f"""
            Here is the csv data:
            This is a general description of the data:
            {self.user_input['general_description']}

            The following is a summary of the data features, data types, and missing values:
            {self.general_info}

            The following is a description of each feature in the data:
            {self.feature_descriptions}

            Here is the initial discovery findings:
            {self.discovery}

            Based upon your knowledge of the data in my .csv and 
            of high-quality Neo4j graph data models, I would like you to return your
            suggestion for translating the data in my .csv into a Neo4j graph data model.
            Focus only on the nodes and relationships. Properties will be added in a later step.

            {model_generation_rules}

            {model_format}
            """
        return prompt

    def _generate_data_model_iteration_prompt(
        self, user_corrections: Union[str, None] = None
    ) -> str:
        """
        Generate the prompt to iterate on the previous data model.
        """

        if user_corrections is not None:
            user_corrections = (
                "Focus on this feedback when refactoring the model: \n"
                + user_corrections
            )
        else:
            user_corrections = """
                                Add features from the csv to each node and relationship as properties. 
                                Ensure that these properties provide value to their respective node or relationship.
                                If a property is a unique identifier, then also add it to the unique_constraints list.
                                """

        prompt = f"""
            Here is the csv data:
            This is a general description of the data:
            {self.user_input['general_description']}

            The following is a summary of the data features, data types, and missing values:
            {self.general_info}

            The following is a description of each feature in the data:
            {self.feature_descriptions}

            Here is the initial discovery findings:
            {self.discovery}

            Based on your experience building high-quality graph data
            models, are there any improvements you would suggest to this model?
            {self.current_model}

            {user_corrections}

            {model_generation_rules}
            """

        return prompt

    def create_initial_model(self) -> str:
        """
        Create the initial model.
        """

        # assert self._discovery_ran, "Run discovery before creating the initial model."

        response = self.llm.get_data_model_response(
            formatted_prompt=self._generate_initial_data_model_prompt(),
            csv_columns=self.columns_of_interest,
        )

        self.model_history.append(response)

        self._initial_model_created = True

        return response

    def iterate_model(
        self, iterations: int = 1, user_corrections: Union[str, None] = None
    ) -> str:
        """
        Iterate on the previous data model the number times indicated.
        """

        assert self._initial_model_created, "No data model present to iterate on."

        def iterate():
            for i in range(0, iterations):
                response = self.llm.get_data_model_response(
                    formatted_prompt=self._generate_data_model_iteration_prompt(
                        user_corrections=user_corrections
                    ),
                    csv_columns=self.columns_of_interest,
                )

                self.model_history.append(response)
                self.model_iterations += 1
                yield response

        for iteration in iterate():
            return iteration
