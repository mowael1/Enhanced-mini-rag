from fastapi import FastAPI
from contextlib import asynccontextmanager
from helpers.config import get_settings
from motor.motor_asyncio import AsyncIOMotorClient

from routes import base, data
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    
    # Mongodb serverده الاتصال الفعلي ب 
    app.mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
    # معينه database هنا بقي انت عاوز تتعامل مع 
    app.db_client = app.mongo_client[settings.MONGODB_DATABASE]
    
    yield 
    app.mongo_client.close()

app = FastAPI(lifespan=lifespan)

app.include_router(base.base_router)
app.include_router(data.data_router)
