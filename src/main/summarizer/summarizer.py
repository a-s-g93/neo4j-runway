from typing import Dict, List
import io

import pandas as pd

from llm.llm import LLM


class Summarizer:

    def __init__(self, llm: LLM, user_input: Dict[str, str], data: pd.DataFrame) -> None:
        self.user_input = user_input
        self.llm = llm

        assert "General Info" in self.user_input.keys(), "user_input must include key:value pair {General Info: ...}"

        self.columns_of_interest = list(user_input.keys())[:1]

        self.data = data[self.columns_of_interest]
    

    def generate_csv_summary(self) -> Dict[str, pd.DataFrame]:
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

        descriptions = ""
        for col in self.description_numeric.columns:
            descriptions += f"{col}: {self.user_input[col]} \n It has the following distribution: {self.description_numeric[col]} \n\n"

        for col in self.description_categorical.columns:
            descriptions += f"{col}: {self.user_input[col]} \n It has the following distribution: {self.description_categorical[col]} \n\n"

        prompt = f"""
                You are a data scientist with experience creating Neo4j
                graph data models from tabular data. I am a developer who will be
                creating a Neo4j graph data model from the data in a single .csv file.

                I want you to perform a preliminary analysis on my data to help us understand
                its characteristics before we brainstorm about the graph data model.

                This is a general description of the data:
                {self.user_input['General Description']}

                The following is summary of the data features, data types, and missing values:
                {self.general_info}

                The following is a description of each feature in the data:
                {descriptions}

                Provide me with your preliminary analysis of this data. What are important
                overall details about the data? What are the most important features?

                Do not return your suggestion for the Neo4j graph data model
                yet. We will do that in the next step.
                """
        
        return prompt
    
    @staticmethod
    def _generate_initial_data_model_prompt() -> str:
        """
        Generate the initial data model request prompt.
        """
        prompt = """
            That is a very helpful. Based upon your of the data in my .csv and your
            knowledge of high-quality Neo4j graph data models, I would like you to return your
            suggestion for translating the data in my .csv into a Neo4j graph data model.

            Once built, the Neo4j graph will be used to identify
            potential fraud. We have not identified fraudulent loans yet
            and so do not have that information in this data.

            Please return the following:
            Suggested Nodes and their properties, along with your reasoning for each
            Relationships and their properties, along with your reasoning for each
            Include only nodes, relationships, and properties derived from
            features from my .csv file.

            Do not return any code to create the data model. I only want to
            focus on the proposed nodes, relationships, and properties with
            your explanation for why you suggested each.

            Return your data model in JSON format. 
            Format nodes as:
            {
                "Label": <node label>,
                "Properties": <list of node properties>,
                "Reasoning": <reasoning for why this decision was made.>
            }
            Format relationships as:
            {
                "Label": <relationship label>,
                "Properties": <list of relationship properties>,
                "From": <the node this relationship begins>,
                "To": <the node this relationship ends>,
                "Reasoning": <reasoning for why this decision was made.>
                }
            """
        return prompt
    
    @staticmethod
    def _generate_data_model_iteration_prompt() -> str:
        """
        Generate the prompt to iterate on the previous data model.
        """

        prompt = """
            That is a good start and very helpful.

            Based on your experience building high-quality graph data
            models, are there any improvements you would suggest?

            For example, are there any node properties that should
            be converted to separate, additional nodes in the data model?

            Please return an updated graph data model with your suggested improvements.
            Reference only features available in the original .csv file.

            Do not return any code to create the data model. I only want to
            focus on the proposed nodes, relationships, and properties.

            Return your data model in JSON format.
            Format nodes as:
            {
                "Label": <node label>,
                "Properties": <list of node properties>,
                "Reasoning": <reasoning for why this decision was made.>
            }
            Format relationships as:
            {
                "Label": <relationship label>,
                "Properties": <list of relationship properties>,
                "From": <the node this relationship begins>,
                "To": <the node this relationship ends>,
                "Reasoning": <reasoning for why this decision was made.>
                }
            """
    
        return prompt
    
    def discovery(self) -> str:
        """
        Run discovery on the data.
        """

        pass

    def initial_model(self) -> str:
        """
        Create the initial model.
        """

        pass

    def iterate_model(self, iterations: int = 1) -> str:
        """
        Iterate on the previous model the number times indicated.
        """

        pass