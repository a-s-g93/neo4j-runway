"""
This file contains the LLM module that interfaces with an OpenAI LLM for data discovery.
"""

import os
from typing import Any, Dict, Optional

import instructor

try:
    import openai
except ImportError:
    openai = None  # type: ignore[unused-ignore, assignment]

from ..base import BaseDiscoveryLLM


class OpenAIDiscoveryLLM(BaseDiscoveryLLM):
    """
    Interface for interacting with different LLMs for data discovery.

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
        model_name: str = "gpt-4o-2024-05-13",
        model_params: Optional[dict[str, Any]] = None,
        open_ai_key: Optional[str] = None,
        enable_async: bool = False,
        llm_init_params: Dict[str, Any] = dict(),
    ) -> None:
        """
        Interface for interacting with OpenAI LLMs for data discovery.

        Parameters
        ----------
        model_name : str
            The name of the model. By default gpt-4o-2024-05-13
        model_params : Optional[dict[str, Any]], optional
            Any parameters to pass to the model for a request, by default None
        open_ai_key: Union[str, None], optional
            Your OpenAI API key if it is not declared in an environment variable. By default None
        enable_async : bool
            Whether to allow asynchronous LLM calls. This may be utilized in multi-csv input to improve response speed. By default False
        llm_init_params : Dict[str, Any], optional
            Parameters to pass to the model during initialization, by default dict()
        """

        if openai is None:
            raise ImportError(
                "Could not import openai python client. "
                "Please install it with `pip install openai`."
            )

        client: Any

        if enable_async:
            client = instructor.from_openai(
                openai.AsyncOpenAI(
                    api_key=(
                        open_ai_key
                        if open_ai_key is not None
                        else os.environ.get("OPENAI_API_KEY")
                    ),
                    **llm_init_params,
                )
            )
        else:
            client = instructor.from_openai(
                openai.OpenAI(
                    api_key=(
                        open_ai_key
                        if open_ai_key is not None
                        else os.environ.get("OPENAI_API_KEY")
                    ),
                    **llm_init_params,
                )
            )

        super().__init__(
            model_name=model_name,
            model_params=model_params,
            client=client,
            is_async=enable_async,
        )
