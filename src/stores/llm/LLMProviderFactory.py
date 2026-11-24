from .providers import OpenAIProvider
from .LLMEnums import LLMEnums

class LLMProviderFactory:
    
    def __init__(self, config: dict):
        self.config = config
        
        
    def create(self, provider: str , api_key: str, api_url: str):
        
        if provider == LLMEnums.OPENAI.value:
            return OpenAIProvider(
                api_key = api_key,
                api_url = api_url
            )
        
        raise ValueError(f"Unknown LLM provider: {provider}")