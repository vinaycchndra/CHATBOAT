import logging
from dataAccessLayer.chat_dal import ChatSessionOdmLayer, ChatMessageOdmLayer
from dataAccessLayer.userDal import UserOdmLayer
from core.exceptions import EntityDoesNotExist, UnAuthorizedAccess, NothingToUpdate
from typing import Dict, List, Any
from dateutil import parser
from models.chatModels import ChatRoles
from services.LLMs_service import GeminiLLM

logger = logging.getLogger("__name__")
class ChatSessionService: 

    @staticmethod
    async def create_chat_session(email: str) -> Dict: 
        # Get user first
        user_object = await UserOdmLayer.get_user(email=email)

        if not user_object: 
            raise EntityDoesNotExist(f"User with email: {email} does not exists.")

        chat_session = await ChatSessionOdmLayer.create_chat_session(user=user_object)
        
        return {
                "session_id": str(chat_session.id), 
                "user_id": str(chat_session.userId.id), 
                "session_summary": chat_session.session_summary, 
                "created_at": str(chat_session.created_at), 
                "updated_at": str(chat_session.updated_at) 
            }

    @staticmethod
    async def get_chat_session(session_id: str, user_id: str) -> Dict: 
        chat_session = await ChatSessionOdmLayer.get_chat_session(session_id)
        user_detail = chat_session.userId.to_dict()
        from_db_user_id = user_detail.get("id")

        if from_db_user_id != user_id: 
            raise UnAuthorizedAccess("You don't have permission to access it.") 
        return {
                "session_id": str(chat_session.id), 
                "user_id": from_db_user_id, 
                "session_summary": chat_session.session_summary, 
                "created_at": str(chat_session.created_at), 
                "updated_at": str(chat_session.updated_at) 
            } 

    @staticmethod
    async def update_chat_session(session_id: str, user_id: str, session_summary: str = None, archive: str = None) -> Dict[str, Any]: 
        chat_session = await ChatSessionOdmLayer.get_chat_session(session_id)

        user_detail = chat_session.userId.to_dict()
        from_db_user_id = user_detail.get("id")
        

        if from_db_user_id != user_id: 
            raise UnAuthorizedAccess("You don't have permission to access it.")

        query = {"session_id": session_id}

        if session_summary is not None: 
            query["session_summary"] = session_summary

        if archive is not None: 
            query["archive"] = archive

        if len(query) == 1: 
            raise NothingToUpdate("Nothing to update for the session object.")
        
        chat_session = await ChatSessionOdmLayer.update_chat_session(**query)

        return  {
                    "session_id": str(chat_session.id), 
                    "user_id": from_db_user_id, 
                    "session_summary": chat_session.session_summary, 
                    "created_at": str(chat_session.created_at), 
                    "updated_at": str(chat_session.updated_at), 
                    "archived": chat_session.archived
                } 

    @staticmethod 
    async def query_chat_sessions(user_id: str, session_ids: List[str] = None, created_at: str = None, updated_at: str= None, archived: bool = None) -> List[Dict]: 
        query = {"user_id": user_id} 

        if created_at: 
            query["created_at"] = parser.parse(created_at, tzinfos={"tzname": "UTC"})

        if updated_at: 
            query["updated_at"] = parser.parse(updated_at, tzinfos={"tzname": "UTC"})

        if archived is not None: 
            query["archived"] = archived

        if session_ids: 
            query["session_ids"] = session_ids

        chat_session_list = await ChatSessionOdmLayer.query_chat_sessions(**query)

        res = []
        for chat_session in chat_session_list: 
            user_detail = chat_session.userId.to_dict()
            from_db_user_id = user_detail.get("id")        
            session_obj = {
                    "session_id": str(chat_session.id), 
                    "user_id": from_db_user_id, 
                    "session_summary": chat_session.session_summary, 
                    "created_at": str(chat_session.created_at), 
                    "updated_at": str(chat_session.updated_at),
                    "archived": chat_session.archived 
                } 
            res.append(session_obj)

        return res

class ChatMessageService: 

    @classmethod
    async def create_messasge(cls, session_id: str, role: str, message_text: str) -> Dict: 
        """
            session_id(str): session to which message belongs
            role(str): either "ai" or "human"
            message_text(str): text
        """

        if role not in ["ai", "human"]:
            raise ValueError("Only two roles are possible.")

        if not message_text: 
            raise ValueError("Message can not be empty")

        message = await ChatMessageOdmLayer.create_message(session_id=session_id, role=role, message_text=message_text)

        # session_detail = message.sessionId.to_dict()
        # from_db_session_id = session_detail.get("id") 
        from_db_session_id =  message.sessionId.id 
        message_dict = {
            "session_id": from_db_session_id, 
            "role": message.role, 
            "message": message.messageText, 
            "is_summarized": message.isSummarized, 
            "created_at": str(message.created_at),
            "updated_at": str(message.updated_at)
        }

        return message_dict

    @classmethod
    async def query_message(cls, 
                            session_id: str, 
                            is_summarized: bool = None,
                            role: str = None, 
                            created_at: str = None, 
                            updated_at: str = None, 
                            limit: int = None, 
                            offset: int = None
                        ) -> List[Dict]: 

        query = {"session_id": session_id}

        if created_at: 
            query["created_at"] = parser.parse(created_at, tzinfos={"tzname": "UTC"})

        if updated_at: 
            query["updated_at"] = parser.parse(updated_at, tzinfos={"tzname": "UTC"})

        if is_summarized is not None: 
            query["is_summarized"] = is_summarized

        if role is not None: 
            if role not in ["ai", "human"]: 
                raise ValueError("Only two types of roles are possible either ai or human.")

            if role == ChatRoles.AI:
                query["role"] = ChatRoles.AI
            elif role == ChatRoles.HUMAN:
                query["role"] = ChatRoles.HUMAN 

        if limit is not None: 
            query["limit"] = limit

        if offset is not None: 
            query["offset"] = offset

        messages = await ChatMessageOdmLayer.query_message(**query)    

        res = []

        for message in messages: 
            from_db_session_id =  message.sessionId.id  #session_detail.get("id") 

            message_dict = {
                "id": message.id, 
                "session_id": from_db_session_id, 
                "role": message.role, 
                "message": message.messageText, 
                "is_summarized": message.isSummarized, 
                "created_at": str(message.created_at),
                "updated_at": str(message.updated_at)
            }

            res.append(message_dict)

        return res 


    @classmethod
    async def summarize_messages(cls, session_id: str, user_id: str) -> bool: 
        try:
            # querying the non summarized messages.
            chat_messages = await cls.query_message(session_id=session_id, is_summarized=False)
            res = []
            message_ids = []
            for i in range(len(chat_messages)-1, -1, -1): 
                chat_message = chat_messages[i]
                res.append((chat_message.get("role").value, chat_message.get("message")))
                message_ids.append(chat_message.get("id"))
            print(message_ids, res, "\n\nthis is the message\n")
            # Query the session summary
            session_object = await ChatSessionService.get_chat_session(session_id=session_id, user_id=user_id)
            session_summary = session_object.get("session_summary")

            if len(res) == 0:
                return False 
            
            updated_session_summary = await GeminiLLM.summariseWithExistingSummary(existingSummary=session_summary, lastNChats=res)

            # update the session summary and update the summarized flag.
            await ChatSessionService.update_chat_session(session_id=session_id, user_id=user_id, session_summary=updated_session_summary)            

            # update the summarized flag of the chat messages
            await ChatMessageOdmLayer.update_messages_status(message_ids=message_ids, is_summarized=True)

        except Exception:
            logger.exception(f"Something happened while summarizing the messages for the session_id: {session_id}")    
        









        # "session_id": from_db_session_id, 
        #                 "role": message.role, 
        #                 "message": message.messageText, 
        #                 "is_summarized": message.isSummarized, 
        #                 "created_at": str(message.created_at),
        #                 "updated_at": str(message.updated_at)