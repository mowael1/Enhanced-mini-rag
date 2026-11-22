from models import BaseDataModel
from models.db_schemes import chunk_scheme
from models.enums import DataBaseEnum
from bson.objectid import ObjectId
from pymongo import InsertOne
from sqlalchemy import select, func,delete

class ChunkModel(BaseDataModel):
    
    def __init__(self, db_client):
        super().__init__(db_client = db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]
        
    async def init_collection(self):
        indexes = chunk_scheme.get_indexes()
        for index in indexes:
            await self.collection.create_index(
                index["key"],
                name=index["name"],
                unique=index["unique"]
            )
            
    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        
        return instance
        
        
    async def create_chunk(self, chunk: chunk_scheme):
        
        result = await self.collection.insert_one(chunk.model_dump(by_alias=True, exclude_unset=True))
        chunk.id = result.inserted_id
        
        return chunk
    
    async def get_chunk(self, chunk_id: str):
        result = await self.collection.find_one({
            "_id": ObjectId(chunk_id)
        })
        
        if result is None: 
            return None
        
        return chunk_scheme(**result)
    
    
    
    async def insert_many_chunks(self, chunks: list, batch_size: int = 100):
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]

            operations = [
                InsertOne(chunk.model_dump(by_alias=True, exclude_unset=True))
                for chunk in batch
            ]

            await self.collection.bulk_write(operations)

        return len(chunks)


    async def delete_chunks_by_project_id(self, project_id: ObjectId):
        
        result = await self.collection.delete_many({
            "chunk_project_id": project_id
        })
        
        return result.deleted_count