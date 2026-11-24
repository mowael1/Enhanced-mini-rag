from fastapi import FastAPI
from contextlib import asynccontextmanager
from helpers.config import get_settings
from motor.motor_asyncio import AsyncIOMotorClient

from stores.llm import LLMProviderFactory
from stores.vectordb import VectorDBProviderFactory

from routes import base, data, nlp
from stores.llm import TemplateParser
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    
    app.mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongo_client[settings.MONGODB_DATABASE]
    
    llm_provider_factory = LLMProviderFactory(settings)
    
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND, api_key=settings.OPENAI_API_KEY,api_url=settings.OPENAI_API_URL)
    app.generation_client.set_generation_model(settings.GENERATION_MODEL_ID)
    
    
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND , api_key=settings.NIVDIA_API_KEY,api_url=settings.NIVDIA_API_URL)

    app.embedding_client.set_embedding_model(model_id= settings.EMBEDDING_MODEL_ID, 
                                            embedding_size=settings.EMBEDDING_MODEL_SIZE)
    
    vectordb_provider_factory = VectorDBProviderFactory(settings)

    # VectorDB client
    app.vectordb_client = vectordb_provider_factory.create(provider=settings.VECTOR_DB_BACKEND)
    app.vectordb_client.connect()
    
    app.template_parser = TemplateParser(settings.PRIMARY_LANG,settings.DEFAULT_LANG)

    yield 
    app.vectordb_client.disconnect()
    app.mongo_client.close()

app = FastAPI(lifespan=lifespan)

app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)
