from .db_schemes import asset_schema
from .BaseDataModel import BaseDataModel
from .enums import DataBaseEnum
from bson import ObjectId

class AssetModel(BaseDataModel):
    
    def __init__(self, db_client):
        super().__init__(db_client= db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_ASSET_NAME.value]
        
    async def init_collection(self):
        indexes = asset_schema.get_indexes()
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

    async def create_asset(self, asset: asset_schema):
        
        result = await self.collection.insert_one(asset.model_dump(by_alias=True, exclude_unset=True))
        asset.id = result.inserted_id
        
        return asset
    
    async def get_all_project_assets(self,asset_project_id: str, asset_type: str):
        
        records =  await self.collection.find({
            "asset_project_id": ObjectId(asset_project_id) if isinstance(asset_project_id,str) else asset_project_id,
            "asset_type": asset_type
        }).to_list(length = None)
        
        return [
            asset_schema(**record)
            for record in records
        ]
        
    async def get_asset_record(self, asset_project_id: str, asset_name: str):
        
        record = await self.collection.find_one({
            "asset_project_id": ObjectId(asset_project_id) if isinstance(asset_project_id,str) else asset_project_id,
            "asset_name": asset_name
        })
        
        if record: 
            return asset_schema(**record)
        
        return None