from fastapi import APIRouter, Request, Depends, BackgroundTasks, UploadFile
from fastapi.responses import JSONResponse
from core.middleware import AuthMiddleware
from core.constants import LOCAL_FILE_STORAGE, FILE_UPLOAD_CHUNK_SIZE
from services.file_metadata_service import FileMetaDataService
from services.EmbeddingService import VectorEmbeddingService 
import aiofiles


file_handling_router = APIRouter(
    prefix="/v1/file",
    dependencies=[Depends(AuthMiddleware.authenticate)],
    tags=["file_handler"],
    responses={404: {"description": "Not found"}},
)

@file_handling_router.post("", tags=["upload_file"])
async def create_file(request: Request, file: UploadFile, background_task: BackgroundTasks):
    user_id = request.state.user_id
    # file name 
    uploaded_file_name = file.filename.lower()

    # file path 
    temp_file_name = user_id+ "_" +uploaded_file_name
    uploaded_file_path = LOCAL_FILE_STORAGE / temp_file_name

    # file type 
    uploaded_file_type = file.content_type.lower()

    # file size
    uploaded_file_size = file.size

    # Checking if a similar file upload is attempted by the user earlier
    file_list = await FileMetaDataService.query_file_metadata(
        user_ids=[user_id], 
        file_types=[uploaded_file_type], 
        file_names = [uploaded_file_name],
        file_size=uploaded_file_size, 
        is_uploaded=True, 
        archived=False
    )

    if len(file_list) > 0:
        return JSONResponse(status_code = 400, content=
                            {"message": "This file is already uploaded, if not please change the name of file and try again."})    
    try:
        async with aiofiles.open(uploaded_file_path, "wb") as f_output:
            while read_chunk := await file.read(FILE_UPLOAD_CHUNK_SIZE): 
                await f_output.write(read_chunk)
    except Exception as e: 
        return JSONResponse(status_code=400, content={"message": str(e)})

    try:
        # creating the file metadata 
        data = await FileMetaDataService.create_file_metadata(
                        user_id=user_id, 
                        file_name=uploaded_file_name, 
                        file_type=uploaded_file_type, 
                        file_path = uploaded_file_path,
                        file_size = uploaded_file_size,
                    )
        # updating the uploaded status as successfull
        data = await FileMetaDataService.update_file_metadata(id = data.get("id"), uploaded=True)   
    except Exception as e: 
        return JSONResponse(status_code=500, content={"message": str(e)})

    # file parsing and vector embeddings for the file and update the processed status.
    background_task.add_task(
        VectorEmbeddingService.createEmbeddingForFile, 
        uploaded_file_type, 
        uploaded_file_path, 
        user_id, 
        data.get("id")
    )
    return JSONResponse(status_code=201, content={"message": "Uploaded Successfully.", "data": data})

