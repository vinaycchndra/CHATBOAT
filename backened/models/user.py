from datetime import datetime, timezone
from pydantic import Field
from beanie import Document, Indexed, before_event, Update, SaveChanges, Replace

class User(Document):
    name: str
    password: str 
    email: Indexed(str, unique=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = False
    is_admin: bool  = False

    @before_event(Update, Replace, SaveChanges)
    def set_updated_at(self):
        self.updated_at = datetime.now(timezone.utc)

    class Settings:
        name = "users"


