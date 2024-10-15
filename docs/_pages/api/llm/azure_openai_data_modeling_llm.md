---
permalink: /api/llm/azure-openai-data-modeling-llm/
title: AzureOpenAIDataModelingLLM
toc: true
toc_label: AzureOpenAIDataModelingLLM
toc_icon: "fa-solid fa-plane"
---

    from neo4j_runway.llm.openai import AzureOpenAIDataModelingLLM


 Interface for interacting with OpenAI LLMs for data
        modeling services.

    Attributes
    ----------
    model_name : str
        The name of the deployment model.
    model_params : Optional[dict[str, Any]], optional
        Any parameters to pass to the model.
    client : Instructor
            An LLM client patched with Instructor.



## Class Methods


### __init__
Interface for interacting with Azure OpenAI LLMs for
        data modeling services.

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
    azure_open_ai_key : Optional[str], optional
        Your Azure OpenAI API key if it is not declared in
        an environment variable as 'AZURE_OPENAI_API_KEY'.
        By default None
    llm_init_params : Dict[str, Any], optional
        Parameters to pass to the model during
        initialization, by default dict()
