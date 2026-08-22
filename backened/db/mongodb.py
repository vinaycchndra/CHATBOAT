import os 
from beanie import init_beanie
from pymongo import AsyncMongoClient
from models.user import User
from models.Models import ChatSession, ChatMessage, FileMetaData

async def initDb():
    # Create Async PyMongo client
    mongoConnectionString = os.getenv("MONGODB_CONNECTION_STRING")
    client = AsyncMongoClient(
        mongoConnectionString, 
        uuidRepresentation="standard"
    )

    await init_beanie(database=client.db_name, document_models=[User, ChatSession, ChatMessage, FileMetaData])