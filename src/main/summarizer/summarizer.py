import io
from typing import Dict, Any, Union

import pandas as pd

from llm.llm import LLM

from resources.prompts.prompts import model_generation_rules, model_format


class Summarizer:

    def __init__(self, llm: LLM, user_input: Dict[str, str], data: pd.DataFrame) -> None:
        self.user_input = user_input
        self.llm = llm

        assert "General Description" in self.user_input.keys(), "user_input must include key:value pair {General Description: ...}"

        self.columns_of_interest = list(user_input.keys())
        self.columns_of_interest.remove("General Description")

        self.data = data[self.columns_of_interest]

        self._discovery_ran = False
        self._initial_model_created = False
        self.model_iterations = 0
        self.model_history = []
    
    @property
    def current_model(self) -> Dict[str, Any]:
        """
        The current data model.
        """

        assert len(self.model_history) > 0, "No models found in history."

        return self.model_history[-1].model_dump()

    @property
    def current_model_viz(self) -> Dict[str, Any]:
        """
        The current data model visualized with Graphviz.
        """

        assert len(self.model_history) > 0, "No models found in history."

        return self.model_history[-1].visualize()
    
    def _generate_csv_summary(self) -> Dict[str, pd.DataFrame]:
        """
        Generate the data summaries.
        """
        buffer = io.StringIO()
        self.data.info(buf=buffer)

        df_info = buffer.getvalue()
        desc_numeric = self.data.describe(percentiles=[0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99])
        desc_categorical = self.data.describe(include='object')

        self.general_info = df_info
        self.description_numeric = desc_numeric
        self.description_categorical = desc_categorical
    
    def _generate_discovery_prompt(self) ->str:
        """
        Generate the initial discovery prompt.
        """

        self._descriptions = ""
        for col in self.description_numeric.columns:
            self._descriptions += f"{col}: {self.user_input[col]} \n It has the following distribution: {self.description_numeric[col]} \n\n"

        for col in self.description_categorical.columns:
            self._descriptions += f"{col}: {self.user_input[col]} \n It has the following distribution: {self.description_categorical[col]} \n\n"

        prompt = f"""
                I want you to perform a preliminary analysis on my data to help us understand
                its characteristics before we brainstorm about the graph data model.

                This is a general description of the data:
                {self.user_input['General Description']}

                The following is a summary of the data features, data types, and missing values:
                {self.general_info}

                The following is a description of each feature in the data:
                {self._descriptions}

                Provide me with your preliminary analysis of this data. What are important
                overall details about the data? What are the most important features?
                """
        
        return prompt
    
    def _generate_initial_data_model_prompt(self) -> str:
        """
        Generate the initial data model request prompt.
        """
        prompt = f"""
            Here is the csv data:
            This is a general description of the data:
            {self.user_input['General Description']}

            The following is a summary of the data features, data types, and missing values:
            {self.general_info}

            The following is a description of each feature in the data:
            {self._descriptions}

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
    
    def _generate_data_model_iteration_prompt(self, user_corrections: Union[str, None] = None) -> str:
        """
        Generate the prompt to iterate on the previous data model.
        """

        if user_corrections is not None:
            user_corrections = "Focus on this feedback when refactoring the model: \n" + user_corrections 
        else:
            user_corrections =  """
                                Add features from the csv to each node and relationship as properties. 
                                Ensure that these properties provide value to their respective node or relationship.
                                If a property is a unique identifier, then also add it to the unique_constraints list.
                                """

        prompt = f"""
            Here is the csv data:
            This is a general description of the data:
            {self.user_input['General Description']}

            The following is a summary of the data features, data types, and missing values:
            {self.general_info}

            The following is a description of each feature in the data:
            {self._descriptions}

            Here is the initial discovery findings:
            {self.discovery}

            Based on your experience building high-quality graph data
            models, are there any improvements you would suggest to this model?
            {self.current_model}

            {user_corrections}

            {model_generation_rules}
            """
    
        return prompt
    
    def run_discovery(self) -> str:
        """
        Run discovery on the data.
        """

        self._generate_csv_summary()
        
        response = self.llm.get_discovery_response(formatted_prompt=self._generate_discovery_prompt())
        
        self._discovery_ran = True
        self.discovery = response

        return response

    def create_initial_model(self) -> str:
        """
        Create the initial model.
        """

        assert self._discovery_ran, "Run discovery before creating the initial model."

        response = self.llm.get_data_model_response(formatted_prompt=self._generate_initial_data_model_prompt(), csv_columns=self.columns_of_interest)

        self.model_history.append(response)

        self._initial_model_created = True

        return response

    def iterate_model(self, iterations: int = 1, user_corrections: Union[str, None] = None) -> str:
        """
        Iterate on the previous model the number times indicated.
        """

        assert self._initial_model_created, "No model present to iterate on."

        def iterate():
            for i in range(0, iterations):
                response = self.llm.get_data_model_response(formatted_prompt=self._generate_data_model_iteration_prompt(user_corrections=user_corrections), csv_columns=self.columns_of_interest)
  
                self.model_history.append(response)
                self.model_iterations+=1
                yield response
        
        for iteration in iterate():
            return iteration