"""
This file contains the LLM module that interfaces with an OpenAI LLM via the Instructor library.
"""

import os
from typing import Any, Dict, List, Union


from openai import OpenAI

import instructor

from ..inputs import UserInput
from ..models import DataModel
from ..resources.prompts import (
    SYSTEM_PROMPTS,
)
from ..resources.prompts.data_modeling import (
    create_retry_data_model_generation_prompt,
    create_initial_data_model_cot_prompt,
    create_initial_data_model_prompt,
)
from ..resources.llm_response_objects import DataModelEntityPool

MODEL_OPTIONS = [
    "gpt-4o",
    "gpt-4o-2024-05-13",
    "gpt-4",
    "gpt-3.5-turbo",
    "gpt-4-0125-preview",
    "gpt-4-turbo-preview",
    "gpt-4-1106-preview",
    "gpt-4-0613",
    "gpt-4-32k",
    "gpt-4-32k-0613",
    "gpt-3.5-turbo-1106",
    "gpt-3.5-turbo-0125",
]


class LLM:
    """
    Interface for interacting with different LLMs.
    """

    def __init__(
        self, model: str = "gpt-4o-2024-05-13", open_ai_key: Union[str, None] = None
    ) -> None:
        """
        Interface for interacting with different LLMs.

        Attributes
        ----------
        model: str, optional
            The OpenAI LLM to use. By default gpt-4o-2024-05-13
        open_ai_key: Union[str, None], optional
            Your OpenAI API key if it is not declared in an environment variable. By default None
        """

        if model not in MODEL_OPTIONS:
            raise ValueError("model must be one of the following: ", MODEL_OPTIONS)
        self.llm_instance = instructor.patch(
            OpenAI(
                api_key=(
                    open_ai_key
                    if open_ai_key is not None
                    else os.environ.get("OPENAI_API_KEY")
                )
            )
        )
        self.model = model

    def _get_discovery_response(self, formatted_prompt: str) -> str:
        """
        Get a discovery response from the LLM.
        """

        response = self.llm_instance.chat.completions.create(
            model=self.model,
            temperature=0,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPTS["discovery"]},
                {"role": "user", "content": formatted_prompt},
            ],
        )
        return response.choices[0].message.content

    def _get_initial_data_model_response(
        self,
        discovery_text: str,
        user_input: UserInput,
        pandas_general_info: str,
        # feature_descriptions: Dict[str, str],
        # allowed_features: List[str],
        max_retries: int = 3,
        use_yaml_data_model: bool = False,
    ) -> Union[DataModel, Dict[str, Any]]:
        """
        Performs at least 2 LLM calls:
            1. Request the LLM to find nodes, relationships and properties that should be in the data model.
            2. Construct and return the data model based on previous recommendations.

        Step 2. may be repeated until max retries is reached or a valid data model is returned.

        Returns
        -------
        DataModel
            The final data model.
        """
        validation = {"valid": False}
        part_one_retries = 0
        # part 1
        while not validation["valid"] and part_one_retries < 2:
            formatted_prompt = create_initial_data_model_cot_prompt(
                discovery_text=discovery_text,
                user_input=user_input,
                allowed_features=user_input.allowed_columns,
            )
            entity_pool: DataModelEntityPool = (
                self.llm_instance.chat.completions.create(
                    model=self.model,
                    temperature=0,
                    response_model=DataModelEntityPool,
                    messages=[
                        {
                            "role": "system",
                            "content": SYSTEM_PROMPTS["initial_data_model"],
                        },
                        {"role": "user", "content": formatted_prompt},
                    ],
                )
            )
            validation = entity_pool.validate(
                allowed_features=user_input.allowed_columns
            )
            part_one_retries += 1

        # part 2
        if validation["valid"]:
            formatted_prompt = create_initial_data_model_prompt(
                discovery_text=discovery_text,
                data_model_recommendations=entity_pool.model_dump(),
                user_input=user_input,
            )

            initial_data_model: DataModel = self._get_data_model_response(
                formatted_prompt=formatted_prompt,
                csv_columns=user_input.allowed_columns,
                max_retries=max_retries,
                use_yaml_data_model=use_yaml_data_model,
            )

            return initial_data_model

        else:
            return validation

    def _get_data_model_response(
        self,
        formatted_prompt: str,
        csv_columns: List[str],
        max_retries: int = 3,
        use_yaml_data_model: bool = False,
    ) -> DataModel:
        """
        Get a data model response from the LLM.
        """

        retries = 0
        valid_response = False
        while retries < max_retries and not valid_response:

            retries += 1  # increment retries each pass

            response: DataModel = self.llm_instance.chat.completions.create(
                model=self.model,
                temperature=0,
                response_model=DataModel,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPTS["data_model"]},
                    {"role": "user", "content": formatted_prompt},
                ],
            )

            validation = response.validate_model(csv_columns=csv_columns)
            if not validation["valid"]:
                print("validation failed")
                cot = self._get_chain_of_thought_for_error_recommendations_response(
                    formatted_prompt=validation["message"]
                )

                formatted_prompt = create_retry_data_model_generation_prompt(
                    chain_of_thought_response=cot,
                    errors_to_fix=validation["errors"],
                    model_to_fix=(
                        response.to_yaml(write_file=False)
                        if use_yaml_data_model
                        else response
                    ),
                )
            elif validation["valid"]:
                print("recieved a valid response")
                valid_response = True

        return response

    def _get_chain_of_thought_for_error_recommendations_response(
        self, formatted_prompt: str
    ) -> str:
        """
        Generate fixes for the previous data model.
        """
        print("performing chain of thought process for error fix recommendations...")
        response = self.llm_instance.chat.completions.create(
            model=self.model,
            temperature=0,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPTS["retry"]},
                {"role": "user", "content": formatted_prompt},
            ],
        )
        return response.choices[0].message.content

    def _get_chain_of_thought_for_initial_model_generation_response(
        self, formatted_prompt: str
    ) -> str:
        """
        Generate nodes, relationships and properties for the previous data model.
        Does NOT return a data model. Only suggestions.
        """
        print(
            "performing chain of thought process for initial data model recommendations..."
        )
        response = self.llm_instance.chat.completions.create(
            model=self.model,
            temperature=0,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPTS["retry"]},
                {"role": "user", "content": formatted_prompt},
            ],
        )
        return response.choices[0].message.content
