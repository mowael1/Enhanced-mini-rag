from fastapi import FastAPI, APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController, ProcessController
from models import ProjectModel, ChunkModel

import aiofiles
import os

from models.enums import ResponseSignal

import logging
from .schema import ProcessRequest
from models.db_schemes import chunk_scheme

logger = logging.getLogger("uvicorn.error")

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1","data"]
)

@data_router.post("/upload/{project_id}")
async def upload_data(request: Request, project_id: str, file: UploadFile, app_settings: Settings = Depends(get_settings)):
    
    """Create Project collection in Mongodb"""
    project_model = ProjectModel(
        db_client=request.app.db_client
    )
    
    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )
    
    """Validate type and size for the file"""
    is_valid, result_signal = DataController().validate_uploaded_file(file=file)
    
    
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": result_signal
            }
        )
        
    file_path, file_id = DataController().generate_file_path(project_id=project_id, file_name=file)

    
    try:
        async with aiofiles.open(file_path, "wb") as f:
            while True:
                chunk = await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE)
                if not chunk:
                    break
                await f.write(chunk)
                
        return JSONResponse(
            status_code= status.HTTP_200_OK,
            content={
                "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
                "file_id": file_id
                }
        )
    except Exception as e:
        
        logger.error(f"Error while uploading file: {e}")
        return JSONResponse(
            status_code= status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.FILE_UPLOAD_FAILED.value
            }
        )
        
        


@data_router.post("/process/{project_id}")
async def process_endpoint(request: Request, project_id: str, process_request: ProcessRequest):
    
    
    """Create Project collection in Mongodb"""
    project_model = ProjectModel(
        db_client=request.app.db_client
    )
    
    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )
    
    chunk_model = ChunkModel(
        db_client=request.app.db_client
    )
    
    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset
    
    if do_reset == 1:
        await chunk_model.delete_chunks_by_project_id(
            project_id= project.id
        )
    
    
    file_chunks = ProcessController(project_id=project_id).process_file_content(
                                    file_id=file_id,chunk_size=chunk_size, 
                                    overlap_size= overlap_size)
    
    if file_chunks is None or len(file_chunks) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "singal": ResponseSignal.PROCESSING_FAILED.value
            }
        )
        
    
    file_chunks_records = [
            chunk_scheme(
                chunk_text= chunk.page_content,
                chunk_metadata= chunk.metadata,
                chunk_order= i+1,
                chunk_project_id=project.id,
            )
            for i, chunk in enumerate(file_chunks)
        ]
    
    
    no_records = await chunk_model.insert_many_chunks(file_chunks_records)

    return JSONResponse(
            status_code= status.HTTP_200_OK,
            content={
                "signal": ResponseSignal.PROCESSING_SUCCESS.value,
                "inserted_chunks": no_records
                }
        )