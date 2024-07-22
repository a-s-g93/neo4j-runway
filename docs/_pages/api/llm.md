---
permalink: /api/llm/
---
# LLM


## Class Methods


__init__
---
Interface for interacting with different LLMs.

    Attributes
    ----------
    model: str, optional
        The OpenAI LLM to use., by default gpt-4o-2024-05-13
    open_ai_key: Union[str, None], optional
        Your OpenAI API key if it is not declared in an
        environment variable., by default None


get_chain_of_thought_response
---
Generate fixes for the previous data model.


get_data_model_response
---
Get a data model response from the LLM.


get_discovery_response
---
Get a discovery response from the LLM.

