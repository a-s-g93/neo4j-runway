# mypy: allow-untyped-defs
"""
This file contains the LLM module that interfaces with an Azure hosted OpenAI LLM for data modeing via the Instructor library.
"""

import os
from typing import Any, Callable, Dict, Optional

try:
    import openai
except ImportError:
    openai = None  # type: ignore[unused-ignore, assignment]

import instructor

from ...base import BaseDataModelingLLM


class AzureOpenAIDataModelingLLM(BaseDataModelingLLM):
    """
    Interface for interacting with OpenAI LLMs for data modeling services.

    Attributes
    ----------
    model_name : str
        The name of the deployment model.
    model_params : Optional[dict[str, Any]], optional
        Any parameters to pass to the model.
    client : Instructor
            An LLM client patched with Instructor.
    """

    def __init__(
        self,
        azure_endpoint: str,
        api_version: str = "2024-07-01-preview",
        azure_ad_token_provider: Optional[Callable[[], str]] = None,
        model: str = "gpt-4o",
        model_params: Optional[dict[str, Any]] = None,
        azure_open_ai_key: Optional[str] = None,
        llm_init_params: Dict[str, Any] = dict(),
    ) -> None:
        """
        Interface for interacting with Azure OpenAI LLMs for data modeling services.

        Parameters
        ----------
        azure_endpoint : str
            The Azure endpoint address.
        api_version : str, optional
            The API version to use, by default 2024-07-01-preview
        azure_ad_token_provider : Optional[Callable[[], str]], optional
            A token to use for Microsoft Entra ID authentication instead of an API key, by default None
        model : str
            The name of the deployment model. By default gpt-4o
        model_params : Optional[dict[str, Any]], optional
            Any parameters to pass to the model for a request, by default None
        azure_open_ai_key : Optional[str], optional
            Your Azure OpenAI API key if it is not declared in an environment variable as 'AZURE_OPENAI_API_KEY'. By default None
        llm_init_params : Dict[str, Any], optional
            Parameters to pass to the model during initialization, by default dict()
        """

        if openai is None:
            raise ImportError(
                "Could not import openai python client. "
                "Please install it with `pip install openai`."
            )

        client = instructor.from_openai(
            openai.AzureOpenAI(
                api_key=(
                    azure_open_ai_key
                    if azure_open_ai_key is not None
                    else os.environ.get("AZURE_OPENAI_API_KEY")
                ),
                api_version=api_version,
                azure_endpoint=azure_endpoint,
                azure_ad_token_provider=azure_ad_token_provider,
                **llm_init_params,
            )
        )

        super().__init__(model_name=model, model_params=model_params, client=client)
