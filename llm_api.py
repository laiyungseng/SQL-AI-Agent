import requests
import json
import os
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama
try:
    from langchain_openai import ChatOpenAI
except ImportError:
    try:
        from langchain_community.chat_models import ChatOpenAI
    except ImportError:
        ChatOpenAI = None

class LLM_API:
    """
    LLM API class to run different service provider.
    """
    def __init__(self, service_provider:str, api_key:str, model_name:str, tools:list, template_prompt,  temperature:float, max_retries:int):
        self.service_provider = service_provider.lower()
        self.api_key = api_key
        self.model_name = model_name
        self.tools = tools
        
        # Handle template_prompt if it's passed as a list of dicts (from JSON load)
        if isinstance(template_prompt, list) and len(template_prompt) > 0 and isinstance(template_prompt[0], dict):
             self.template_prompt = template_prompt[0].get("template", "")
        elif isinstance(template_prompt, str):
             self.template_prompt = template_prompt
        else:
             self.template_prompt = str(template_prompt)

        self.temperature = temperature
        self.max_retries = max_retries
    
    def _run_local_llm(self):
        """
        Run local llm with function calling.

        Returns:
            Runnable: The compiled graph agent.
        """
        model = ChatOllama(
            model = self.model_name,
            temperature = self.temperature,
            max_retries = self.max_retries,
        )
        return create_react_agent(
            model=model,
            tools=self.tools,
            prompt=self.template_prompt,
        )
    
    def _openrouter_llm(self):
        """
        Run openrouter llm with function calling.

        Returns:
            Runnable: The compiled graph agent.
        """
        if ChatOpenAI is None:
            raise ImportError("langchain-openai or langchain-community is required for OpenRouter. Please install `langchain-openai`.")

        model = ChatOpenAI(
            model=self.model_name,
            api_key=self.api_key,
            base_url="https://openrouter.ai/api/v1",
            temperature=self.temperature,
            max_retries=self.max_retries,
        )
        return create_react_agent(
            model=model,
            tools=self.tools,
            prompt=self.template_prompt,
        )
    
    def run_llm(self):
        """
        Select the service provider to run the llm.

        Returns:
            Runnable: The selected service provider agent.
        """
        if self.service_provider == "local" or self.service_provider == "ollama":
            return self._run_local_llm()
        elif self.service_provider == "openrouter":
            return self._openrouter_llm()
        else:
            raise ValueError(f"Invalid service provider: {self.service_provider}")


def get_openrouter_model_list(api_key):
    """
    function to get openrouter model list.

    Args:
        api_key (str): The API key for authentication.

    Returns:
        List: the list of model names.
    """
    url = "https://openrouter.ai/api/v1/models"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        

        if response.status_code == 200:
            models_data = response.json().get('data', [])
            # Return list of model IDs, filtering for those that support 'tools'
            supported_models = []
            for model in models_data:
                # Check 'supported_parameters' (preferred) or 'description' as fallback if needed
                # Based on inspection, 'supported_parameters' contains 'tools'
                params = model.get('supported_parameters', [])
                if params and 'tools' in params:
                    supported_models.append(model['id'])
            
            return supported_models
        else:
            print(f"Failed to fetch models: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"Error fetching OpenRouter models: {e}")
        return []