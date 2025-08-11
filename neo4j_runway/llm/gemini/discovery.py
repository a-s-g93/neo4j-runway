"""
This file contains the LLM module that interfaces with a Google Gemini LLM for data discovery.
"""

import os
from typing import Any, Dict, Optional

import instructor

try:
    import google.generativeai as genai
except ImportError:
    genai = None  # type: ignore[unused-ignore, assignment]

from ..base import BaseDiscoveryLLM


class GeminiDiscoveryLLM(BaseDiscoveryLLM):
    """
    Interface for interacting with Google Gemini LLMs for data discovery.

    Attributes
    ----------
    model_name : str
        The name of the model.
    model_params : Optional[dict[str, Any]], optional
        Any parameters to pass to the model.
    is_async : bool
        Whether the client supports asynchronous API calls.
    client : Instructor
            An LLM client patched with Instructor.
    """

    def __init__(
        self,
        model_name: str = "gemini-1.5-pro",
        model_params: Optional[dict[str, Any]] = None,
        api_key: Optional[str] = None,
        enable_async: bool = False,
        llm_init_params: Dict[str, Any] = {},
    ) -> None:
        """
        Interface for interacting with Google Gemini LLMs for data discovery.

        Parameters
        ----------
        model_name : str
            The name of the model. By default gemini-1.5-pro
        model_params : Optional[dict[str, Any]], optional
            Any parameters to pass to the model for a request, by default None
        api_key: Union[str, None], optional
            Your Google Gemini API key if it is not declared in an environment variable. By default None
        enable_async : bool
            Whether to allow asynchronous LLM calls. This may be utilized in multi-csv input to improve response speed. By default False
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

        client: Any

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
            use_async=enable_async,
        )

        super().__init__(
            model_name=model_name,
            model_params=model_params,
            client=client,
            is_async=enable_async,
        )

    def _get_discovery_response(self, formatted_prompt: str) -> str:
        """
        Get a discovery response from the LLM using Gemini-specific implementation.
        """
        from ...resources.llm_response_types import DiscoveryResponse
        from ...resources.prompts import SYSTEM_PROMPTS

        # For Gemini, model parameters are already configured in the model
        response: DiscoveryResponse = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPTS["discovery"]},
                {"role": "user", "content": formatted_prompt},
            ],
            response_model=DiscoveryResponse,
        )

        return response.response

    async def _get_async_discovery_response(
        self, formatted_prompt: str
    ) -> str:
        """
        Get an async discovery response from the LLM using Gemini-specific implementation.
        """
        from ...resources.llm_response_types import DiscoveryResponse
        from ...resources.prompts import SYSTEM_PROMPTS

        # For Gemini, model parameters are already configured in the model
        response: DiscoveryResponse = await self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPTS["discovery"]},
                {"role": "user", "content": formatted_prompt},
            ],
            response_model=DiscoveryResponse,
        )

        return response.response
