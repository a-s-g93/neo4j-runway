import os
from typing import List, Dict, Tuple, Union

from openai import OpenAI
# import openai
import instructor

# import pandas as pd
from objects.data_model import DataModel
from resources.prompts.prompts import system_prompts

class LLM():
    """
    Interface for interacting with different LLMs.
    """
    
    def __init__(self, open_ai_key: Union[str, None] = None) -> None:

        self.llm_instance = instructor.patch(OpenAI(api_key=open_ai_key if open_ai_key is not None else os.environ.get("OPENAI_API_KEY")))

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
        
    def get_data_model_response(self, formatted_prompt: str, csv_columns: List[str], max_retries: int = 2) -> DataModel:
        """
        Get a data model response from the LLM.
        """

        retries = 0
        valid_response = False
        while retries < max_retries and not valid_response:

            retries+=1 # increment retries each pass

            response = self.llm_instance.chat.completions.create(
                model="gpt-3.5-turbo",
                temperature=0,
                response_model=DataModel,
                messages=[
                    {"role": "system", "content": system_prompts['data_model']},
                    {"role": "user", "content": formatted_prompt}
                ],
            )

            validation = response.validate_model(csv_columns=csv_columns)
            if not validation['valid']:
                print("validation failed")
                formatted_prompt = validation['message']
            elif validation['valid']:
                print("recieved a valid response")
                valid_response = True
            
        return response
