---
permalink: /api/llm/openai-data-modeling-llm/
title: OpenAIDataModelingLLM
toc: true
toc_label: OpenAIDataModelingLLM
toc_icon: "fa-solid fa-plane"
---

    from neo4j_runway.llm.openai import OpenAIDataModelingLLM


 Interface for interacting with OpenAI LLMs for data
        modeling services.

    Attributes
    ----------
    model_name : str
        The name of the model.
    model_params : Optional[dict[str, Any]], optional
        Any parameters to pass to the model.
    client : Instructor
            An LLM client patched with Instructor.



## Class Methods


### __init__
Interface for interacting with OpenAI LLMs for data
        modeling services.

    Parameters
    ----------
    model_name : str
        The name of the model. By default gpt-4o-2024-05-13
    model_params : Optional[dict[str, Any]], optional
        Any parameters to pass to the model for a request,
        by default None
    open_ai_key : Optional[str], optional
        Your OpenAI API key if it is not declared in an
        environment variable. By default None
    llm_init_params : Dict[str, Any], optional
        Parameters to pass to the model during
        initialization, by default dict()
