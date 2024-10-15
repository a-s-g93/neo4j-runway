"""
This file contains the base LLM class that all other LLM classes must inherit from.
"""

import json
from abc import ABC
from typing import Any, Dict, List, Optional, Union

from instructor import Instructor
from instructor.exceptions import InstructorRetryException
from tenacity import Retrying, stop_after_attempt

from ..models import DataModel
from ..models.core.node import Nodes
from ..resources.llm_response_types import (
    DiscoveryResponse,
    ErrorRecommendations,
)
from ..resources.prompts import (
    SYSTEM_PROMPTS,
)
from ..resources.prompts.data_modeling import (
    create_initial_data_model_prompt,
    create_initial_nodes_prompt,
)
from .context import create_context


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

        context = create_context(
            data_dictionary=data_dictionary,
            valid_columns=valid_columns,
            allow_duplicate_column_mappings=allow_duplicate_properties,
            enforce_uniqueness=enforce_uniqueness,
        )
        formatted_prompt = create_initial_nodes_prompt(
            discovery_text=discovery_text,
            multifile=multifile,
            data_dictionary=data_dictionary,
            use_cases=use_cases,
            valid_columns=valid_columns,
        )

        try:
            nodes: Nodes = self.client.chat.completions.create(
                model=self.model_name,
                response_model=Nodes,
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPTS["initial_nodes"],
                    },
                    {"role": "user", "content": formatted_prompt},
                ],
                validation_context=context,
                max_retries=max_retries,
                **self.model_params,
            )

            print("Received Valid Initial Nodes.")
        except InstructorRetryException as e:
            print("Invalid `Nodes` returned.")
            # return model without validation
            nodes: Nodes = Nodes.model_construct(  # type: ignore
                json.loads(
                    e.last_completion.choices[-1]
                    .message.tool_calls[-1]
                    .function.arguments
                )
            )
        print(nodes)

        formatted_prompt = create_initial_data_model_prompt(
            discovery_text=discovery_text,
            data_model_recommendations=nodes,
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

    def _get_data_model_response(
        self,
        formatted_prompt: str,
        valid_columns: dict[str, list[str]],
        data_dictionary: Dict[str, Any],
        max_retries: int = 3,
        use_yaml_data_model: bool = False,
        allow_duplicate_properties: bool = False,
        enforce_uniqueness: bool = True,
        apply_neo4j_naming_conventions: bool = True,
        allow_parallel_relationships: bool = False,
    ) -> DataModel:
        """
        Get a data model response from the LLM.
        """

        context = create_context(
            data_dictionary=data_dictionary,
            valid_columns=valid_columns,
            allow_duplicate_column_mappings=allow_duplicate_properties,
            enforce_uniqueness=enforce_uniqueness,
            apply_neo4j_naming_conventions=apply_neo4j_naming_conventions,
            allow_parallel_relationships=allow_parallel_relationships,
        )

        retry_logic = Retrying(
            stop=stop_after_attempt(max_retries),
            before=lambda _: print("New Data Model Generation Attempt..."),
        )

        try:
            response: DataModel = self.client.chat.completions.create(
                model=self.model_name,
                response_model=DataModel,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPTS["data_model"]},
                    {"role": "user", "content": formatted_prompt},
                ],
                validation_context=context,
                max_retries=retry_logic,
                **self.model_params,
            )
        except InstructorRetryException as e:
            print("Invalid `DataModel` returned.")
            # return model without validation
            return DataModel.model_construct(
                json.loads(
                    e.last_completion.choices[-1]
                    .message.tool_calls[-1]
                    .function.arguments
                )
            )

        return response
