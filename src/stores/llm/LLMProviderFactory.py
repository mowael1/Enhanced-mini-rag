from .providers import OpenAIProvider
from .LLMEnums import LLMEnums

class LLMProviderFactory:
    
    def __init__(self, config: dict):
        self.config = config
        
        
    def create(self, provider: str):
        
        if provider == LLMEnums.OPENAI.value:
            return OpenAIProvider(
                api_key = self.config.OPENAI_API_KEY,
                api_url = self.config.OPENAI_API_URL
            )
        
        raise ValueError(f"Unknown LLM provider: {provider}")