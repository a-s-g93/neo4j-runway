---
permalink: /api/llm/azure-openai-discovery-llm/
title: AzureOpenAIDiscoveryLLM
toc: true
toc_label: AzureOpenAIDiscoveryLLM
toc_icon: "fa-solid fa-plane"
---

    from neo4j_runway.llm.openai import AzureOpenAIDiscoveryLLM


  Interface for interacting with different LLMs for data
        discovery.

     Attributes
     ----------
    model_name : str
         The name of the deployment model.
     model_params : Optional[dict[str, Any]], optional
         Any parameters to pass to the model.
     client : Instructor
             An LLM client patched with Instructor.
     is_async : bool
         Whether the client supports asynchronous API calls.



## Class Methods


### __init__
Interface for interacting with OpenAI LLMs for data
        discovery.

    Parameters
    ----------
    azure_endpoint : str
        The Azure endpoint address.
    api_version : str, optional
        The API version to use, by default
        2024-07-01-preview
    azure_ad_token_provider : Optional[Callable[[], str]],
        optional
        A token to use for Microsoft Entra ID authentication
        instead of an API key, by default None
    model : str
        The name of the deployment model. By default gpt-4o
    model_params : Optional[dict[str, Any]], optional
        Any parameters to pass to the model for a request,
        by default None
    azure_open_ai_key: Union[str, None], optional
        Your OpenAI API key if it is not declared in an
        environment variable as 'AZURE_OPENAI_API_KEY'. By
        default None
    enable_async : bool
        Whether to allow asynchronous LLM calls. This may be
        utilized in multi-csv input to improve response
        speed. By default False
    llm_init_params : Dict[str, Any], optional
        Parameters to pass to the model during
        initialization, by default dict()
