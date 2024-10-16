"""
This file contains the base LLM class that all other LLM classes must inherit from.
"""

import json
from abc import ABC
from typing import Any, Dict, List, Optional

from instructor import Instructor
from instructor.exceptions import InstructorRetryException

from ..models import DataModel
from ..models.core.node import Nodes
from ..resources.llm_response_types import (
    DiscoveryResponse,
)
from ..resources.prompts import (
    SYSTEM_PROMPTS,
)
from ..resources.prompts.data_modeling import (
    create_initial_data_model_prompt,
    create_initial_nodes_prompt,
)
from ..utils._utils.print_formatters import bold, cyan, green, pretty_list, red
from .context import create_context
from .retry import create_retry_logic


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
        allow_duplicate_properties: bool = False,
        enforce_uniqueness: bool = True,
        allow_parallel_relationships: bool = False,
        apply_neo4j_naming_conventions: bool = True,
    ) -> DataModel:
        """
        Performs at least 2 LLM calls:
            1. Request the LLM to find nodes and properties that should be in the data model.
            2. Create Relationships and return the data model based on previous recommendations.

        Step 2. may be repeated until max retries is reached or a valid data model is returned.

        Returns
        -------
        DataModel
            The final data model.
        """

        nodes_prompt = create_initial_nodes_prompt(
            discovery_text=discovery_text,
            multifile=multifile,
            data_dictionary=data_dictionary,
            use_cases=use_cases,
            valid_columns=valid_columns,
        )

        nodes = self._get_nodes_response(
            formatted_prompt=nodes_prompt,
            data_dictionary=data_dictionary,
            valid_columns=valid_columns,
            max_retries=max_retries,
            allow_duplicate_properties=allow_duplicate_properties,
            enforce_uniqueness=enforce_uniqueness,
            apply_neo4j_naming_conventions=apply_neo4j_naming_conventions,
        )

        data_model_prompt = create_initial_data_model_prompt(
            discovery_text=discovery_text,
            data_model_recommendations=nodes,
            multifile=multifile,
            data_dictionary=data_dictionary,
            use_cases=use_cases,
            advanced_rules=use_advanced_data_model_generation_rules,
            valid_columns=valid_columns,
        )

        initial_data_model: DataModel = self._get_data_model_response(
            formatted_prompt=data_model_prompt,
            valid_columns=valid_columns,
            max_retries=max_retries,
            data_dictionary=data_dictionary,
            allow_duplicate_properties=allow_duplicate_properties,
            enforce_uniqueness=enforce_uniqueness,
            allow_parallel_relationships=allow_parallel_relationships,
            apply_neo4j_naming_conventions=apply_neo4j_naming_conventions,
        )

        if not hasattr(initial_data_model, "nodes") and hasattr(nodes, "nodes"):
            initial_data_model.nodes = nodes.nodes

        return initial_data_model

    def _get_data_model_response(
        self,
        formatted_prompt: str,
        valid_columns: dict[str, list[str]],
        data_dictionary: Dict[str, Any],
        max_retries: int = 3,
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

        retry_logic = create_retry_logic(max_retries=max_retries)

        print(bold("> Generating Data Model..."))
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
            print(f"\nReceived {green('Valid')} Data Model")
        except InstructorRetryException as e:
            print(f"\nReceived {red('Invalid')} Data Model")
            # return model without validation
            response: DataModel = DataModel.model_construct(  # type: ignore
                json.loads(
                    e.last_completion.choices[-1]
                    .message.tool_calls[-1]
                    .function.arguments
                )
            )

        if hasattr(response, "nodes"):
            print(
                pretty_list(
                    header="Nodes",
                    content=[cyan(n.__str__()) for n in response.nodes],
                    cols=2,
                ),
                "\n",
            )

        if hasattr(response, "relationships"):
            print(
                pretty_list(
                    header="Relationships",
                    content=[cyan(r.__str__()) for r in response.relationships],
                )
            )

        return response

    def _get_nodes_response(
        self,
        formatted_prompt: str,
        valid_columns: dict[str, list[str]],
        data_dictionary: Dict[str, Any],
        max_retries: int = 3,
        allow_duplicate_properties: bool = False,
        enforce_uniqueness: bool = True,
        apply_neo4j_naming_conventions: bool = True,
    ) -> Nodes:
        """
        Get a nodes response from the LLM.
        """

        context = create_context(
            data_dictionary=data_dictionary,
            valid_columns=valid_columns,
            allow_duplicate_column_mappings=allow_duplicate_properties,
            enforce_uniqueness=enforce_uniqueness,
            apply_neo4j_naming_conventions=apply_neo4j_naming_conventions,
            allow_parallel_relationships=False,
        )

        retry_logic = create_retry_logic(max_retries=max_retries)

        print(bold("> Generating Nodes..."))
        try:
            response: Nodes = self.client.chat.completions.create(
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
                max_retries=retry_logic,
                **self.model_params,
            )

            print(f"\nReceived {green('Valid')} Nodes")
        except InstructorRetryException as e:
            print(f"\nReceived {red('Invalid')} Nodes")
            # return model without validation
            response: Nodes = Nodes.model_construct(  # type: ignore
                json.loads(
                    e.last_completion.choices[-1]
                    .message.tool_calls[-1]
                    .function.arguments
                )
            )

        print(
            pretty_list(
                header="Nodes",
                content=[cyan(n.__str__()) for n in response.nodes],
                cols=2,
            ),
            "\n",
        )

        return response
