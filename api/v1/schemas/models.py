from pydantic import BaseModel, EmailStr
from typing import Optional, List
from enum import Enum

# User Model
class UserLogin(BaseModel): 
    email: EmailStr 
    password: str 


class UserRegister(BaseModel): 
    email: EmailStr
    name: str 
    password: str

# Chat Session Model.
class ChatSessionModel(BaseModel): 
    session_ids: Optional[List[str]]            = None 
    session_summary: str                        = ""
    created_at: Optional[str]                   = None 
    updated_at: Optional[str]                   = None 
    user_id: Optional[str]                      = None 
    archived: Optional[bool]                    = None

# Chat message roles 
class ChatModelRoles(Enum): 
    AI = "ai"
    HUMAN = "human"

# Chat Message Model
class MessageModel(BaseModel): 
    role: Optional[ChatModelRoles] = None 
    message_text: str 
    is_summarized: Optional[bool] = None
    