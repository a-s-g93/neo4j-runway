import os
from typing import List, Dict, Tuple

from langchain.chains import ConversationChain
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from langchain.memory import ConversationTokenBufferMemory
from langchain.schema import HumanMessage


import pandas as pd
from pydantic import BaseModel

class LLM():
    """
    Interface for interacting with different LLMs.
    """

    def __init__(self) -> None:
        # self.llm_instance = AzureChatOpenAI(
        #         openai_api_version=os.environ.get('OPENAI_API_VERSION'),
        #         api_key = os.environ.get('AZURE_OPENAI_API_KEY'),
        #         azure_endpoint = os.environ.get('openai_endpoint'),
        #         azure_deployment = os.environ.get('gpt4_8k_name'),
        #         model_name = 'gpt-4-8k',
        #         temperature=0) # default is 0.7
        self.llm_instance = ChatOpenAI(api_key=os.environ.get("OPENAI_API_KEY"), 
                                       model="gpt-4-0613",
                                       temperature=0)

    
        self.memory = ConversationTokenBufferMemory(llm=self.llm_instance, max_token_limit=1000)

        self.conversation_chain = ConversationChain(llm=self.llm_instance, memory=self.memory)

    def get_response(self, formatted_prompt: str) -> str:
        """
        Get a response from the LLM.
        """

        return self.conversation_chain.predict(input=formatted_prompt)