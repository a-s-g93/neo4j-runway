import io
import json
import regex as re
from typing import Dict, List, Any, Union

import pandas as pd

from llm.llm import LLM


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

        return self.model_history[-1]
    
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
            That is a very helpful. Based upon your knowledge of the data in my .csv and 
            of high-quality Neo4j graph data models, I would like you to return your
            suggestion for translating the data in my .csv into a Neo4j graph data model.

            Please return the following:
            Suggested Nodes and their properties, along with your reasoning for each
            Relationships and their properties, along with your reasoning for each
            Include only nodes, relationships, and properties derived from
            features from my .csv file.

            Do not return any code to create the data model. I only want to
            focus on the proposed nodes, relationships, properties and constraints with
            your explanation for why you suggested each. 
            Properties should be exact matches to features in the .csv file.

            Return your data model in JSON format. Note the start and end of JSON with ```.
            Only include the JSON between the ```.
            Format nodes as:
            {
                "Label": <node label>,
                "Properties": <list of node properties>,
                "Unique Constraints": <list of properties with uniqueness constraints>,
                "Reasoning": <reasoning for why this decision was made.>
            }
            Format relationships as:
            {
                "Type": <relationship type>,
                "Properties": <list of relationship properties>,
                "Unique Constraints": <list of properties with uniqueness constraints>,
                "From": <the node this relationship begins>,
                "To": <the node this relationship ends>,
                "Reasoning": <reasoning for why this decision was made.>
                }
            Format your JSON as:
            {
            "Nodes": {nodes},
            "Relationships"{relationships}
            }
            """
        return prompt
    
    def _generate_data_model_iteration_prompt(self) -> str:
        """
        Generate the prompt to iterate on the previous data model.
        """

        prompt = """
            That is a good start and very helpful.

            Based on your experience building high-quality graph data
            models, are there any improvements you would suggest to this model?
            {data_model}

            For example, are there any node properties that should
            be converted to separate, additional nodes in the data model?

            Please return an updated graph data model with your suggested improvements.
            Properties should be exact matches to features in the .csv file.

            Do not return any code to create the data model. I only want to
            focus on the proposed nodes, relationships, properties and constraints.
            Properties should be exact matches to features in the .csv file.

            Return your data model in JSON format. Note the start and end of JSON with ```.
            Only include the JSON between the ```.
            Format nodes as:
            {{
                "Label": <node label>,
                "Properties": <list of node properties>,
                "Unique Constraints": <list of properties with uniqueness constraints>,
                "Reasoning": <reasoning for why this decision was made.>
            }}
            Format relationships as:
            {{
                "Type": <relationship type>,
                "Properties": <list of relationship properties>,
                "Unique Constraints": <list of properties with uniqueness constraints>,
                "From": <the node this relationship begins>,
                "To": <the node this relationship ends>,
                "Reasoning": <reasoning for why this decision was made.>
                }}
            Format your JSON as:
            {{
            "Nodes": {{nodes}},
            "Relationships"{{relationships}}
            }}
            """.format(data_model=self.current_model)
    
        return prompt
    
    def run_discovery(self) -> str:
        """
        Run discovery on the data.
        """

        self._generate_csv_summary()
        
        response = self.llm.get_response(formatted_prompt=self._generate_discovery_prompt())
        
        self._discovery_ran = True

        return response

    def create_initial_model(self) -> str:
        """
        Create the initial model.
        """

        assert self._discovery_ran, "Run discovery before creating the initial model."

        response = self.llm.get_response(formatted_prompt=self._generate_initial_data_model_prompt())
        validation = self._validate_properties_exist_in_csv(data_model=self.parse_model_from_response(response))
        if not validation['valid']:
            response = self.retry(retry_message=validation["message"])

        self.model_history.append(self.parse_model_from_response(response))

        self._initial_model_created = True

        return response

    def iterate_model(self, iterations: int = 1) -> str:
        """
        Iterate on the previous model the number times indicated.
        """

        assert self._initial_model_created, "No model present to iterate on."

        def iterate():
            for i in range(0, iterations):
                response = self.llm.get_response(formatted_prompt=self._generate_data_model_iteration_prompt())
                validation = self._validate_properties_exist_in_csv(data_model=self.parse_model_from_response(response))
                if not validation['valid']:
                    response = self.retry(retry_message=validation["message"])
                self.model_history.append(self.parse_model_from_response(response))
                self.model_iterations+=1
                yield response
        
        for iteration in iterate():
            return iteration

    def parse_model_from_response(self, response: str) -> Dict[str, Any]:
        """
        Get the model from a response. Assumes ```json\n{...} \n``` format
        """

        try:
            # return json.loads(re.findall(r"(?:```\njson|```json|```)\n(\{[\n\s\w\"\:\[\]\{\\},\'\.\-]*)```", response)[0])
            return json.loads(re.findall(r"(\{[\n\s\w\"\:\[\]\{\\},\'\.\-]*)", response)[0])
        except Exception as e:
            print(response)
            raise ValueError("Unable to parse json from the provided response.")
        
    def _validate_properties_exist_in_csv(self, data_model: Dict[str, Any]) -> Dict[str, Union[bool, str]]:
        """
        Validate that the proposed properties given by the LLM match to the CSV column names.
        """
        print("Validating response...")
        valid = True
        message = ""
        for node in data_model['Nodes']:
            for prop in node['Properties']:
                if prop not in self.columns_of_interest:
                    valid = False
                    print(prop)
                    message+=f"The node {node['Label']} was given the property {prop} which is not present in the provided CSV data. "
        for edge in data_model['Relationships']:
            for prop in node['Properties']:
                if prop not in self.columns_of_interest:
                    valid = False
                    print(prop)
                    message+=f"The relationship {edge['Type']} was given the property {prop} which is not present in the provided CSV data. "
        
        if message != "":
            # print("pre formatted message: ", message)
            message = """
                        The following issues are present in the current model: {input} Fix the errors.
                        Return your data model in JSON format. Note the start and end of JSON with ```.
                        Only include the JSON between the ```.
                        Format nodes as:
                        {{
                            "Label": <node label>,
                            "Properties": <list of node properties>,
                            "Unique Constraints": <list of properties with uniqueness constraints>,
                            "Reasoning": <reasoning for why this decision was made.>
                        }}
                        Format relationships as:
                        {{
                            "Type": <relationship type>,
                            "Properties": <list of relationship properties>,
                            "Unique Constraints": <list of properties with uniqueness constraints>,
                            "From": <the node this relationship begins>,
                            "To": <the node this relationship ends>,
                            "Reasoning": <reasoning for why this decision was made.>
                            }}
                        Format your JSON as:
                        {{
                        "Nodes": {{nodes}},
                        "Relationships"{{relationships}}
                        }}
                        """.format(input=str(message))

        return {"valid": valid, "message": message}
    
    def retry(self, retry_message: str, max_retries = 1) -> str:
        """
        Receive a new LLM response with fixed errors.
        """
        retries = 0
        valid = False
        while retries > max_retries and not valid:
            print("retry: ", retries+1)
            response = self.llm.get_response(formatted_prompt=retry_message)
            validation = self._validate_properties_exist_in_csv(data_model=self.parse_model_from_response(response))
            valid = validation["valid"]
            retry_message = validation["message"]
            retries+=1

        if retries >= max_retries and not valid:
            print("Max retries reached to properly format JSON.")
            return response
        
        return response
        
