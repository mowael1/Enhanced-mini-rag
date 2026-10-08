from fastapi import FastAPI
from contextlib import asynccontextmanager
from helpers.config import get_settings


settings = get_settings()

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    
    yield 