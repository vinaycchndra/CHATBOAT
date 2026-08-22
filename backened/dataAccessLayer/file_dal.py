import logging
from models.Models import FileMetaData
from models.user import User
from beanie.operators import In
from beanie import PydanticObjectId
from uuid import UUID
from core.exceptions import EntityDoesNotExist
from typing import List
from datetime import datetime

logger = logging.getLogger("__name__")

class FileMetaDataDal: 

    @classmethod
    async def create_file_metadata(cls, file_name: str, file_type: str, file_path: str, file_size: int, user: User) -> FileMetaData:
        file_type = file_type.lower()
        file_name = file_name.lower()
        try:
            file_meta_obj = FileMetaData(file_name = file_name, file_path=str(file_path), file_size=file_size, userId = user, file_type=file_type) 
            file_meta_obj = await file_meta_obj.save()
        except Exception: 
            logger.exception("Something happend while creating the metadata for uploaded file.")
            raise 
        return file_meta_obj

    @classmethod
    async def update_file_metadata(cls, id: str, uploaded: bool = None, processed: bool = None, archived: bool = None) -> FileMetaData:
        try: 
            file_metadata_obj = await FileMetaData.find_one(FileMetaData.id == UUID(hex = id))
            if not file_metadata_obj:
                raise EntityDoesNotExist(f"File with id: {id} does not exist.") 

            if uploaded is not None:
                file_metadata_obj.uploaded = uploaded

            if processed is not None: 
                file_metadata_obj.processed = processed 

            if archived is not None: 
                file_metadata_obj.archived = archived 

            file_metadata_obj = await file_metadata_obj.save()
        except Exception: 
            logger.exception("Something happended while querying the file id.")
            raise 

        return file_metadata_obj

    @classmethod
    async def query_file_metadata(cls, 
                                        ids: List[str] = None,
                                        file_paths: List[str] = None,
                                        user_ids: List[str] = None, 
                                        file_types: List[str] = None, 
                                        file_names: List[str] = None,  
                                        created_at: datetime = None, 
                                        updated_at: datetime = None, 
                                        is_uploaded: bool = None, 
                                        file_size: int = None, 
                                        archived: bool = None
                                    ) -> List[FileMetaData]: 

        query_odm = FileMetaData.find()

        if ids is not None and len(ids) > 0: 
            ids = [UUID(id) for id in ids]
            query_odm = query_odm.find(In(FileMetaData.userId.id, ids))

        if user_ids and len(user_ids) > 0:
            user_ids = [PydanticObjectId(user_id) for user_id in user_ids] 
            query_odm = query_odm.find(In(FileMetaData.userId.id, user_ids),  fetch_links=True)

        if file_paths and len(file_paths) > 0:
            query_odm = query_odm.find(In(FileMetaData.file_path, file_paths))

        if file_types and len(file_types) > 0:
            file_types = [file_type.lower() for file_type in file_types] 
            query_odm = query_odm.find(In(FileMetaData.file_type, file_types))

        if file_names and len(file_names) > 0: 
            file_names = [file_name.lower() for file_name in file_names]
            query_odm = query_odm.find(In(FileMetaData.file_name, file_names))

        if is_uploaded is not None: 
            query_odm = query_odm.find(FileMetaData.uploaded == is_uploaded)

        if file_size is not None: 
            query_odm = query_odm.find(FileMetaData.file_size == file_size)

        if archived is not None: 
            query_odm = query_odm.find(FileMetaData.archived == archived) 
        
        if created_at: 
            query_odm = query_odm.find({"created_at": {"$gte": created_at}})

        if updated_at: 
            query_odm = query_odm.find({"updated_at": {"$gte": updated_at}})

        try:
            file_metadata_list = await query_odm.sort("-created_at").to_list() 
        except Exception: 
            logger.exception("Something happend while querying file metadata")
            raise 

        return file_metadata_list
