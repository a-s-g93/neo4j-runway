# mypy: allow-untyped-defs
"""
This file contains the LLM module that interfaces with a Google Gemini LLM for data modeling via the Instructor library.
"""

import os
from typing import Any, Dict, Optional

try:
    import google.generativeai as genai
except ImportError:
    genai = None  # type: ignore[unused-ignore, assignment]

import instructor

from ..base import BaseDataModelingLLM


class GeminiDataModelingLLM(BaseDataModelingLLM):
    """
    Interface for interacting with Google Gemini LLMs for data modeling services.

    Attributes
    ----------
    model_name : str
        The name of the model.
    model_params : Optional[dict[str, Any]], optional
        Any parameters to pass to the model.
    client : Instructor
            An LLM client patched with Instructor.
    """

    def __init__(
        self,
        model_name: str = "gemini-1.5-pro",
        model_params: Optional[dict[str, Any]] = None,
        api_key: Optional[str] = None,
        llm_init_params: Dict[str, Any] = {},
    ) -> None:
        """
        Interface for interacting with Google Gemini LLMs for data modeling services.

        Parameters
        ----------
        model_name : str
            The name of the model. By default gemini-1.5-pro
        model_params : Optional[dict[str, Any]], optional
            Any parameters to pass to the model for a request, by default None
        api_key : Optional[str], optional
            Your Google Gemini API key if it is not declared in an environment variable. By default None
        llm_init_params : Dict[str, Any], optional
            Parameters to pass to the model during initialization, by default {}
        """

        if genai is None:
            raise ImportError(
                "Could not import google.generativeai python client. "
                "Please install it with `pip install google-generativeai`."
            )

        # Configure the API key
        api_key_to_use = (
            api_key
            if api_key is not None
            else os.environ.get("GEMINI_API_KEY")
        )
        
        if api_key_to_use is None:
            raise ValueError(
                "Gemini API key must be provided either through the api_key parameter "
                "or the GEMINI_API_KEY environment variable."
            )
        
        genai.configure(api_key=api_key_to_use)

        # Prepare generation config from model_params
        generation_config = {}
        if model_params:
            # Map common parameters to Gemini's generation config
            if "temperature" in model_params:
                generation_config["temperature"] = model_params["temperature"]
            if "max_tokens" in model_params:
                generation_config["max_output_tokens"] = model_params["max_tokens"]
            if "top_p" in model_params:
                generation_config["top_p"] = model_params["top_p"]
            if "top_k" in model_params:
                generation_config["top_k"] = model_params["top_k"]

        # Create the Gemini model with generation config
        gemini_model = genai.GenerativeModel(
            model_name, 
            generation_config=generation_config if generation_config else None,
            **llm_init_params
        )
        
        # Create client using instructor with JSON mode for better schema compatibility
        client = instructor.from_gemini(
            gemini_model,
            mode=instructor.Mode.GEMINI_JSON,
        )

        super().__init__(
            model_name=model_name,
            model_params=model_params,
            client=client,
        )

    def _get_data_model_response(
        self,
        formatted_prompt: str,
        valid_columns: dict[str, list[str]],
        data_dictionary: "DataDictionary",
        max_retries: int = 3,
        allow_duplicate_properties: bool = False,
        enforce_uniqueness: bool = True,
        apply_neo4j_naming_conventions: bool = True,
        allow_parallel_relationships: bool = False,
    ) -> "DataModel":
        """
        Get a data model response from the LLM using Gemini-specific implementation.
        """
        from ..context import create_context
        from ..retry import create_retry_logic
        from ...resources.prompts import SYSTEM_PROMPTS
        from ...models import DataModel
        from ...utils._utils.print_formatters import bold, cyan, green, red, pretty_list
        from instructor.exceptions import InstructorRetryException
        import json

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
            # For Gemini, we don't pass the model parameter since it's already configured in the client
            response: DataModel = self.client.chat.completions.create(
                response_model=DataModel,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPTS["data_model"]},
                    {"role": "user", "content": formatted_prompt},
                ],
                validation_context=context,
                max_retries=retry_logic,
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
            print(e.messages)

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
        data_dictionary: "DataDictionary",
        max_retries: int = 3,
        allow_duplicate_properties: bool = False,
        enforce_uniqueness: bool = True,
        apply_neo4j_naming_conventions: bool = True,
    ) -> "Nodes":
        """
        Get a nodes response from the LLM using Gemini-specific implementation.
        """
        from ..context import create_context
        from ..retry import create_retry_logic
        from ...resources.prompts import SYSTEM_PROMPTS
        from ...models.core.node import Nodes
        from ...utils._utils.print_formatters import bold, cyan, green, red, pretty_list
        from instructor.exceptions import InstructorRetryException
        import json

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
            # For Gemini, we don't pass the model parameter since it's already configured in the client
            response: Nodes = self.client.chat.completions.create(
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
