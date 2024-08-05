"""
This file contains the LLM module that interfaces with an OpenAI LLM for data discovery.
"""

import os
from typing import Any, Optional, Union

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
    open_ai_key: Union[str, None], optional
        Your OpenAI API key if it is not declared in an environment variable.
    enable_async : bool
        Whether to allow asynchronous LLM calls. This may be utilized in multi-csv input to improve response speed.
    kwargs : Any
        Parameters to pass to the model during initialization.
    """

    def __init__(
        self,
        model_name: str = "gpt-4o-2024-05-13",
        model_params: Optional[dict[str, Any]] = None,
        open_ai_key: Union[str, None] = None,
        enable_async: bool = False,
        **kwargs: Any,
    ) -> None:
        """
        Interface for interacting with OpenAI LLMs for data discovery.

        Parameters
        ----------
        model_name : str
            The name of the model. By default gpt-4o-2024-05-13
        model_params : Optional[dict[str, Any]], optional
            Any parameters to pass to the model, by default None
        open_ai_key: Union[str, None], optional
            Your OpenAI API key if it is not declared in an environment variable. By default None
        enable_async : bool
            Whether to allow asynchronous LLM calls. This may be utilized in multi-csv input to improve response speed. By default False
        kwargs : Any
            Parameters to pass to the model during initialization.
        """

        if openai is None:
            raise ImportError(
                "Could not import openai python client. "
                "Please install it with `pip install openai`."
            )

        client: Any

        if enable_async:
            client = openai.AsyncOpenAI(
                api_key=(
                    open_ai_key
                    if open_ai_key is not None
                    else os.environ.get("OPENAI_API_KEY")
                ),
                **kwargs,
            )
        else:
            client = openai.OpenAI(
                api_key=(
                    open_ai_key
                    if open_ai_key is not None
                    else os.environ.get("OPENAI_API_KEY")
                ),
                **kwargs,
            )

        super().__init__(
            model_name=model_name, model_params=model_params, client=client
        )
