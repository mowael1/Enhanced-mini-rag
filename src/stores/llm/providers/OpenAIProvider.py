from ..LLMInterface import LLMInterface
from ..LLMEnums import OpenAIEnums
from openai import OpenAI
import logging
from helpers.config import get_settings

class OpenAIProvider(LLMInterface):
# Every Provider will have their own __init__() function
    def __init__(self, api_key: str, api_url: str= None,
                default_input_max_char: int= 1000,
                default_generation_max_output_tokens: int= 1000,
                default_generation_temperature: float = .1):
        
        self.api_key = api_key
        self.api_url = api_url
        
        self.settings = get_settings()
        
        self.default_input_max_char = default_input_max_char
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature

        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        self.client = OpenAI(
            api_key= self.api_key,
            base_url= self.api_url,
        )
                
        self.logger = logging.getLogger(__name__)
        self.enums = OpenAIEnums
        
    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id
        
    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size
        
    def construct_prompt(self, prompt: str, role: str):
        return {"role": role, "content": prompt}
    
    def generate_text(self, prompt: str,chat_history: list = [], max_output_tokens: int = None, temperature: float= None):
        
        chat_history = chat_history.copy() if chat_history else [] 

        if not self.client:
            self.logger.error("OpenAI was not set")
            return None
        
        if not self.generation_model_id:
            self.logger.error("Generation model for OpenAI was not set")
            return None
        
        max_output_tokens = max_output_tokens or self.default_generation_max_output_tokens
        temperature = temperature or self.default_generation_temperature
        
        chat_history.append(self.construct_prompt(prompt=prompt, role=OpenAIEnums.USER.value))
        
        response = self.client.chat.completions.create(
            model=self.generation_model_id,
            messages=chat_history,
            max_tokens=max_output_tokens,
            temperature=temperature)
        
        if not response or not response.choices or len(response.choices) == 0 or not response.choices[0].message:
            
            self.logger.error("Error while generating text with OpenAI")
            return None
        
        return response.choices[0].message.content
        
    def embed_text(
        self,
        texts: list[str],
        document_type: str = "passage"
    ):

        if not self.client:
            self.logger.error("OpenAI client was not set")
            return None

        if not self.embedding_model_id:
            self.logger.error("Embedding model was not set")
            return None

        if document_type not in ("passage", "query"):
            raise ValueError("document_type must be 'passage' or 'query'")

        if not texts or any(
            not isinstance(text, str) or not text.strip()
            for text in texts
        ):
            self.logger.error("Invalid or empty texts")
            return None

        response = self.client.embeddings.create(
            model=self.embedding_model_id,
            input=texts,
            dimensions=self.embedding_size,
            extra_body={
                "input_type": document_type
            }
        )

        if (
            not response
            or not response.data
            or len(response.data) != len(texts)
            or any(not item.embedding for item in response.data)
        ):
            self.logger.error("Error while embedding texts")
            return None

        embeddings = [
            item.embedding
            for item in sorted(response.data, key=lambda item: item.index)
        ]

        return embeddings
