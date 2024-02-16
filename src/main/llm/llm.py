import os
from typing import List, Dict, Tuple, Union

# from langchain.chains import ConversationChain
# from langchain_openai import AzureChatOpenAI, ChatOpenAI
# from langchain.memory import ConversationTokenBufferMemory
# from langchain.schema import HumanMessage
from openai import OpenAI
import openai
import instructor

import pandas as pd
from objects.data_model import DataModel
from resources.prompts.prompts import system_prompts

class LLM():
    """
    Interface for interacting with different LLMs.
    """

    # def __init__(self) -> None:
        # self.llm_instance = AzureChatOpenAI(
        #         openai_api_version=os.environ.get('OPENAI_API_VERSION'),
        #         api_key = os.environ.get('AZURE_OPENAI_API_KEY'),
        #         azure_endpoint = os.environ.get('openai_endpoint'),
        #         azure_deployment = os.environ.get('gpt4_8k_name'),
        #         model_name = 'gpt-4-8k',
        #         temperature=0) # default is 0.7

    
        # self.memory = ConversationTokenBufferMemory(llm=self.llm_instance, max_token_limit=1000)

        # self.conversation_chain = ConversationChain(llm=self.llm_instance, memory=self.memory)
    
    def __init__(self) -> None:

        self.llm_instance = instructor.patch(OpenAI(api_key=os.environ.get("OPENAI_API_KEY")))

    def get_discovery_response(self, formatted_prompt: str) -> DataModel:
        """
        Get a discovery response from the LLM.
        """

        response = self.llm_instance.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0,
            messages=[
                {"role": "system", "content": system_prompts['discovery']},
                {"role": "user", "content": formatted_prompt}
            ]
        )
        return response.choices[0].message.content
        
    def get_data_model_response(self, formatted_prompt: str) -> str:
        """
        Get a data model response from the LLM.
        """

        response = self.llm_instance.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0,
            response_model=DataModel,
            messages=[
                {"role": "system", "content": system_prompts['data_model']},
                {"role": "user", "content": formatted_prompt}
            ]
        )
        return response