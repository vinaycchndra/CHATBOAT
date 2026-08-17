from pydantic import BaseModel, EmailStr
from typing import Optional, List

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



