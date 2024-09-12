"""
This file contains the base LLM class that all other LLM classes must inherit from.
"""

from abc import ABC
from typing import Any, Dict, List, Optional, Union

from instructor import Instructor

from ..inputs import UserInput
from ..models import DataModel
from ..resources.llm_response_types import (
    DataModelEntityPool,
    DiscoveryResponse,
    ErrorRecommendations,
)
from ..resources.prompts import (
    SYSTEM_PROMPTS,
)
from ..resources.prompts.data_modeling import (
    create_data_model_iteration_prompt,
    create_initial_data_model_cot_prompt,
    create_initial_data_model_prompt,
    create_retry_data_model_generation_prompt,
)


class BaseDiscoveryLLM(ABC):
    """
    The base class for interacting with different LLMs. All DiscoveryLLM classes must inherit from this class.
    """

    def __init__(
        self,
        model_name: str,
        client: Instructor,
        is_async: bool = False,
        model_params: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        The base DiscoveryLLM class.

        Parameters
        ----------
        model_name : str
            The name of the model.
        model_params : Optional[dict[str, Any]], optional
            Any parameters to pass to the model, by default None
        client : Instructor
            An LLM client patched with Instructor.
        is_async : bool
            Whether async calls may be made, by default False
        """

        self.model_name = model_name
        self.model_params = model_params or dict()
        if "temperature" not in self.model_params.keys():
            self.model_params["temperature"] = 0
        self.client = client
        self.is_async = is_async

    def _get_discovery_response(self, formatted_prompt: str) -> str:
        """
        Get a discovery response from the LLM.
        """

        response: DiscoveryResponse = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPTS["discovery"]},
                {"role": "user", "content": formatted_prompt},
            ],
            response_model=DiscoveryResponse,
            **self.model_params,
        )

        return response.response

    async def _get_async_discovery_response(
        self, formatted_prompt: str
    ) -> DiscoveryResponse:
        """
        Get an async discovery response from the LLM.
        """

        response: DiscoveryResponse = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPTS["discovery"]},
                {"role": "user", "content": formatted_prompt},
            ],
            response_model=DiscoveryResponse,
            **self.model_params,
        )
        return response


class BaseDataModelingLLM(ABC):
    """
    The base DataModelingLLM class for interacting with different LLMs. All DataModelingLLM classes must inherit from this class.
    """

    def __init__(
        self,
        model_name: str,
        client: Instructor,
        model_params: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        The base DataModelingLLM class.

        Parameters
        ----------
        model_name : str
            The name of the model.
        model_params : Optional[dict[str, Any]], optional
            Any parameters to pass to the model, by default None
        client : Instructor
            An LLM client patched with Instructor.
        """

        self.model_name = model_name
        self.model_params = model_params or dict()
        if "temperature" not in self.model_params.keys():
            self.model_params["temperature"] = 0
        self.client = client

    def _get_initial_data_model_response(
        self,
        discovery_text: str,
        valid_columns: Dict[str, List[str]],
        use_cases: str,
        multifile: bool,
        use_advanced_data_model_generation_rules: bool,
        data_dictionary: Dict[str, Any],
        max_retries: int = 3,
        use_yaml_data_model: bool = False,
        allow_duplicate_properties: bool = False,
        enforce_uniqueness: bool = True,
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
            print(f"Entity Pool Generation Attempt: {part_one_retries+1}")
            formatted_prompt = create_initial_data_model_cot_prompt(
                discovery_text=discovery_text,
                multifile=multifile,
                data_dictionary=data_dictionary,
                use_cases=use_cases,
                valid_columns=valid_columns,
            )
            entity_pool: DataModelEntityPool = self.client.chat.completions.create(
                model=self.model_name,
                response_model=DataModelEntityPool,
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPTS["initial_data_model"],
                    },
                    {"role": "user", "content": formatted_prompt},
                ],
                **self.model_params,
            )
            validation = entity_pool.validate_pool(
                valid_columns=valid_columns, data_dictionary=data_dictionary
            )
            part_one_retries += 1
            # print(entity_pool)
        # part 2
        if validation["valid"]:
            print("Received Valid Entity Pool.")

            formatted_prompt = create_initial_data_model_prompt(
                discovery_text=discovery_text,
                data_model_recommendations=entity_pool,
                multifile=multifile,
                data_dictionary=data_dictionary,
                use_cases=use_cases,
                advanced_rules=use_advanced_data_model_generation_rules,
                valid_columns=valid_columns,
            )

            initial_data_model: DataModel = self._get_data_model_response(
                formatted_prompt=formatted_prompt,
                valid_columns=valid_columns,
                max_retries=max_retries,
                use_yaml_data_model=use_yaml_data_model,
                data_dictionary=data_dictionary,
                allow_duplicate_properties=allow_duplicate_properties,
                enforce_uniqueness=enforce_uniqueness,
            )

            return initial_data_model

        else:
            return validation

    def _get_data_model_response(
        self,
        formatted_prompt: str,
        valid_columns: dict[str, list[str]],
        data_dictionary: Dict[str, Any],
        max_retries: int = 3,
        use_yaml_data_model: bool = False,
        allow_duplicate_properties: bool = False,
        enforce_uniqueness: bool = True,
    ) -> DataModel:
        """
        Get a data model response from the LLM.
        """

        retries = 0
        valid_response = False

        while retries < max_retries and not valid_response:
            retries += 1  # increment retries each pass

            response: DataModel = self.client.chat.completions.create(
                model=self.model_name,
                response_model=DataModel,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPTS["data_model"]},
                    {"role": "user", "content": formatted_prompt},
                ],
                **self.model_params,
            )

            validation = response.validate_model(
                valid_columns=valid_columns,
                data_dictionary=data_dictionary,
                allow_duplicate_properties=allow_duplicate_properties,
                enforce_uniqueness=enforce_uniqueness,
            )
            if not validation["valid"]:
                print(
                    "validation failed\nNumber of Errors: ",
                    len(validation["errors"]),
                    "\n",
                )
                # print(validation["message"])
                cot = self._get_chain_of_thought_for_error_recommendations_response(
                    formatted_prompt=validation["message"]
                )

                formatted_prompt = create_retry_data_model_generation_prompt(
                    chain_of_thought_response=cot,
                    errors_to_fix=validation["errors"],
                    model_to_fix=response,
                    multifile=len(valid_columns.keys()) > 1,
                    data_dictionary=data_dictionary,
                    valid_columns=valid_columns,
                    use_yaml_data_model=use_yaml_data_model,
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
        print("Analyzing errors...")
        response: ErrorRecommendations = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPTS["retry"]},
                {"role": "user", "content": formatted_prompt},
            ],
            response_model=ErrorRecommendations,
            **self.model_params,
        )
        return response.recommendations
