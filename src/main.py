from fastapi import FastAPI
from contextlib import asynccontextmanager
from helpers.config import get_settings
from motor.motor_asyncio import AsyncIOMotorClient

from stores.llm import LLMProviderFactory

from routes import base, data
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    
    app.mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongo_client[settings.MONGODB_DATABASE]
    
    llm_provider_factory = LLMProviderFactory(settings)
    
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(settings.GENERATION_MODEL_ID)
    
    
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id= settings.EMBEDDING_MODEL_ID, 
                                            embedding_size=settings.EMBEDDING_MODEL_SIZE)
    
    yield 
    app.mongo_client.close()

app = FastAPI(lifespan=lifespan)

app.include_router(base.base_router)
app.include_router(data.data_router)
