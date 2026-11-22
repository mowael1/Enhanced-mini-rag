from .BaseDataModel import BaseDataModel
from .enums import DataBaseEnum
from .db_schemes import project_scheme

class ProjectModel(BaseDataModel):
    
    def __init__(self, db_client):
        super().__init__(db_client= db_client)
        
        # Here we have project collection in mongodb
        self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]
        
    
    # For apply indexing
    async def init_collection(self):
        indexes = project_scheme.get_indexes()
        for index in indexes:
            await self.collection.create_index(
                index["key"],
                name=index["name"],
                unique=index["unique"]
            )
            
            
    @classmethod
    async def create_instance(cls, db_client: object):
        """We will use this function to make object from the model and applay indexing"""
        
        # This will call the __init__()
        instance = cls(db_client)
        
        # Here we applying indexing
        await instance.init_collection()
        
        return instance
        
    async def create_project(self, project:project_scheme):
        
        # Convert pydantic model into dictionary
        # We added these parameters to not send (id) because it's null right now
        data = project.model_dump(by_alias=True, exclude={"id"})
        
        # Add dictionary(project) into collection
        # After adding dict it will return an object
        result = await self.collection.insert_one(data)
        
        project.id = result.inserted_id
        
        return project
    
    
    async def get_project_or_create_one(self, project_id: str):
        
        # It will return dictionary or None
        record = await self.collection.find_one({
            "project_id": project_id
        })
        
        if record is None:
            project = project_scheme(project_id=project_id)
            
            result = await self.create_project(project=project)
            
            return result
        
        return project_scheme(**record)
    
    # We get all projects by Pagination
    async def get_all_projects(self, page: int = 1, page_size: int = 10):
    
        total_documents = await self.collection.count_documents({})
        
        skip = (page - 1) * page_size

        cursor = self.collection.find({}).skip(skip).limit(page_size)
        
        projects = []
        async for project in cursor:
            projects.append(project_scheme(**project))
            
        
        return projects, total_documents