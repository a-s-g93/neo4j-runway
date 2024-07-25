---
permalink: /api/llm/
title: LLM
toc: true
toc_label: LLM
toc_icon: "fa-solid fa-plane"
---

    from neo4j_runway import LLM




## Class Methods


### __init__
Interface for interacting with different LLMs.

    Attributes
    ----------
    model: str, optional
        The OpenAI LLM to use. By default gpt-4o-2024-05-13
    open_ai_key: Union[str, None], optional
        Your OpenAI API key if it is not declared in an
        environment variable. By default None

