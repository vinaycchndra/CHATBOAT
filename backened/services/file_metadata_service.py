import logging
from dateutil import parser
from typing import Dict, List
from dataAccessLayer.file_dal import FileMetaDataDal 
from dataAccessLayer.userDal import UserOdmLayer
from models.Models import FileMetaData
from core.exceptions import EntityDoesNotExist

logger = logging.getLogger(__name__)

class FileMetaDataService: 

    @classmethod
    async def create_file_metadata(cls, user_id: str, file_name: str, file_type: str, file_path: str, file_size: int) -> Dict: 
        user_object = await UserOdmLayer.get_user(user_id = user_id)

        if not user_object: 
            raise EntityDoesNotExist(f"User with user_id: {user_id} does not exist.")

        obj = await FileMetaDataDal.create_file_metadata(
                                                    file_name = file_name, 
                                                    file_type=file_type, 
                                                    file_path = file_path, 
                                                    file_size = file_size, 
                                                    user=user_object
                                                )
        return cls.__get_response_payload(obj)

    @classmethod
    async def update_file_metadata(cls, id: str, uploaded: bool = None, processed: bool = None, archived: bool = None) -> Dict: 
        obj = await FileMetaDataDal.update_file_metadata(id=id, uploaded=uploaded, processed=processed, archived=archived)
        return cls.__get_response_payload(obj)

    @classmethod
    async def query_file_metadata(cls, 
                                  ids: List[str] = None, 
                                  file_paths: List[str] = None, 
                                  user_ids: List[str] = None,
                                  file_types: List[str] = None,
                                  file_names: List[str] = None,  
                                  file_size: int = None,
                                  archived: bool = None,  
                                  created_at: str = None, 
                                  updated_at: str = None,
                                  is_uploaded: bool = None  
                                ) -> List[Dict]: 
        query = dict() 

        if ids is not None and len(ids) > 0: 
            query["ids"] = ids 

        if file_types is not None and len(file_types) > 0: 
            query["file_types"] = file_types

        if file_paths is not None and len(file_paths) > 0: 
            query["file_paths"] = file_paths

        if file_names is not None and len(file_names) > 0: 
            query["file_names"] = file_names

        if user_ids is not None and len(user_ids) > 0: 
            query["user_ids"] = user_ids

        if is_uploaded is not None: 
            query["is_uploaded"] = is_uploaded

        if file_size is not None: 
            query["file_size"] = file_size

        if archived is not None: 
            query["archived"] = archived

        if created_at: 
            query["created_at"] = parser.parse(created_at, tzinfos={"tzname": "UTC"})

        if updated_at: 
            query["updated_at"] = parser.parse(updated_at, tzinfos={"tzname": "UTC"})

        if len(query) == 0:
            return []

        file_metadata_list = await FileMetaDataDal.query_file_metadata(
            **query
            )

        res = []
        for file_metadata in file_metadata_list: 
            res.append(cls.__get_response_payload(file_metadata))

        return res


    @classmethod
    def __get_response_payload(cls, obj: FileMetaData) -> Dict: 
        return {
            "id": str(obj.id),
            "file_name": obj.file_name, 
            "file_size": obj.file_size, 
            "uploaded": obj.uploaded, 
            "processed": obj.processed,  
            "created_at": str(obj.created_at), 
            "updated_at": str(obj.updated_at), 
        }
