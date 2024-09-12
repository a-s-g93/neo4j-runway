# mypy: allow-untyped-defs
"""
This file contains the LLM module that interfaces with an OpenAI LLM for data modeing via the Instructor library.
"""

import os
from typing import Any, Dict, Optional

try:
    import openai
except ImportError:
    openai = None  # type: ignore[unused-ignore, assignment]

import instructor

from ..base import BaseDataModelingLLM


class OpenAIDataModelingLLM(BaseDataModelingLLM):
    """
    Interface for interacting with OpenAI LLMs for data modeling services.

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
        model_name: str = "gpt-4o-2024-05-13",
        model_params: Optional[dict[str, Any]] = None,
        open_ai_key: Optional[str] = None,
        llm_init_params: Dict[str, Any] = dict(),
    ) -> None:
        """
        Interface for interacting with OpenAI LLMs for data modeling services.

        Parameters
        ----------
        model_name : str
            The name of the model. By default gpt-4o-2024-05-13
        model_params : Optional[dict[str, Any]], optional
            Any parameters to pass to the model for a request, by default None
        open_ai_key : Optional[str], optional
            Your OpenAI API key if it is not declared in an environment variable. By default None
        llm_init_params : Dict[str, Any], optional
            Parameters to pass to the model during initialization, by default dict()
        """

        if openai is None:
            raise ImportError(
                "Could not import openai python client. "
                "Please install it with `pip install openai`."
            )

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
            model_name=model_name, model_params=model_params, client=client
        )
