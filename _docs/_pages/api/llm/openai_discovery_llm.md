---
permalink: /api/llm/openai-discovery-llm/
title: OpenAIDiscoveryLLM
toc: true
toc_label: OpenAIDiscoveryLLM
toc_icon: "fa-solid fa-plane"
---

    from neo4j_runway.llm.openai import OpenAIDiscoveryLLM


 Interface for interacting with different LLMs for data
        discovery.

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



## Class Methods


### __init__
Interface for interacting with OpenAI LLMs for data
        discovery.

    Parameters
    ----------
    model_name : str
        The name of the model. By default gpt-4o-2024-05-13
    model_params : Optional[dict[str, Any]], optional
        Any parameters to pass to the model for a request,
        by default None
    open_ai_key: Union[str, None], optional
        Your OpenAI API key if it is not declared in an
        environment variable. By default None
    enable_async : bool
        Whether to allow asynchronous LLM calls. This may be
        utilized in multi-csv input to improve response
        speed. By default False
    llm_init_params : Dict[str, Any], optional
        Parameters to pass to the model during
        initialization, by default dict()
