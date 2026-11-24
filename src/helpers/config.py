from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    
    APP_NAME: str
    APP_VERSION: str
    
    FILE_ALLOWED_TYPES: list
    FILE_MAX_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE: int
    
    MONGODB_URL: str
    MONGODB_DATABASE:str
    
    # POSTGRES_USER: str
    # POSTGRES_PASSWORD: str
    # POSTGRES_HOST: str
    # POSTGRES_PORT: int
    # POSTGRES_MAIN_DATABASE: str
    # # ====================== LLM Config ======================
    GENERATION_BACKEND: str
    EMBEDDING_BACKEND: str

    OPENAI_API_KEY: str
    OPENAI_API_URL: str
    
    NIVDIA_API_KEY: str
    NIVDIA_API_URL: str
    
    
    GENERATION_MODEL_ID: str
    EMBEDDING_MODEL_ID: str
    EMBEDDING_MODEL_SIZE: int
    
    
    VECTOR_DB_BACKEND: str
    VECTOR_DB_PATH : str
    VECTOR_DB_DISTANCE_METHOD: str
    limit_documents: int
    
    class Config:
        env_file = ".env"
        
        
def get_settings():
    return Settings()