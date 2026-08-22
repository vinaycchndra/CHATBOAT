from datetime import datetime, timezone
from pydantic import Field
from beanie import Document, Link, Indexed, before_event, Update, SaveChanges, Replace, Save
from models.user import User
from uuid import UUID, uuid4
from enum import Enum

# Chat session
class ChatSession(Document):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    session_summary: str = ""
    userId : Link[User]
    archived: bool = False

    @before_event(Update, Replace, SaveChanges, Save)
    def set_updated_at(self):
        self.updated_at = datetime.now(timezone.utc)

    class Settings:
        name = "chat_session"


class ChatRoles(str, Enum):
    AI = "ai"
    HUMAN = "human"

# Chat Message
class ChatMessage(Document): 
    sessionId: Link[ChatSession]
    role: ChatRoles
    messageText: str
    isSummarized: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @before_event(Update, Replace, SaveChanges, Save)
    def set_updated_at(self):
        self.updated_at = datetime.now(timezone.utc)

    class Settings:
        name = "chat"

# uploaded file metadata.
class FileMetaData(Document): 
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    file_name: str
    file_path: Indexed(str, unique = True) 
    file_type:str
    file_size: int 
    userId : Link[User]
    uploaded: bool = False
    processed: bool = False
    archived: bool = False

    @before_event(Update, Replace, SaveChanges, Save)
    def set_updated_at(self):
        self.updated_at = datetime.now(timezone.utc)

    class Settings:
        name = "file_metadata"
    