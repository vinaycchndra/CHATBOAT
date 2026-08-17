import logging
from models.chatModels import ChatSession
from models.user import User
from uuid import UUID
from core.exceptions import EntityDoesNotExist
from typing import List
from datetime import datetime
from beanie import PydanticObjectId

logger = logging.getLogger(__name__)

class ChatSessionOdmLayer: 

    @staticmethod
    async def create_chat_session(user: User, session_summary: str = "") -> ChatSession: 
        try:
            chat_session = ChatSession(userId=user, session_summary=session_summary)
            await chat_session.insert()
        except Exception as e: 
            logger.exception(f"Something happend while creating the chat session for the user_id: {str(user.id)}")
            raise e
        return chat_session

    @staticmethod
    async def get_chat_session(session_id:str) -> ChatSession: 
        try:
            chat_session = await ChatSession.find_one({"_id": UUID(hex=session_id)})
            if not chat_session:  
                raise EntityDoesNotExist(f"session: {session_id} does not exist.")
        except Exception as e: 
            logger.exception(f"Something happend while fetching session.")
            raise e
        return chat_session

    @staticmethod
    async def query_chat_sessions(
                            user_id: str,
                            session_ids: List[str] = None, 
                            created_at: datetime = None, 
                            updated_at: datetime = None,  
                            archived: bool = None
                    ) -> List[ChatSession]: 

        """
            args: 
                session_ids: List of session_ids
                created_at: datetime -> object, results filtered for greater than the created_at date.
                updated_at: datetime -> object, results filtered for greater than the updated_at date.
                user_id: str ->  User who owns the sessions.    
            
            result: List of chat sessions ordered by created_at date.
        
        """
        query = {"userId.$id" : PydanticObjectId(user_id)}

        if session_ids and len(session_ids) > 0:
            session_ids = [UUID(session_id) for session_id in session_ids] 
            query["_id"] = {"$in": session_ids} 

        if created_at: 
            query["created_at"] = {"$gt": created_at}

        if updated_at: 
            query["updated_at"] = {"$gt": updated_at}

        if archived is not None: 
            query["archived"] = archived 

        try:
            chat_sessions = await ChatSession.find(query).sort("-created_at").to_list(None) 
        except Exception: 
            logger.exception("Something happend while querying chat sessions.")
            raise 

        return chat_sessions

    @staticmethod
    async def update_chat_session(session_id: str, session_summary: str = None, archive: bool = None) -> ChatSession: 
        try:
            chat_session = await ChatSession.find_one({"_id": UUID(hex=session_id)})
            if not chat_session: 
                raise EntityDoesNotExist(f"session: {session_id} does not exist.")

            if archive is not None: 
                chat_session.archived = archive

            if session_summary is not None: 
                chat_session.session_summary = session_summary

            chat_session = await chat_session.save()                

        except Exception as e: 
            logger.exception(f"Something happend while fetching session and updating it.")
            raise e
        return chat_session
