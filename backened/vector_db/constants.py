import os
from dotenv import load_dotenv

load_dotenv()

VECTOR_DB_HOST=os.getenv("VECTOR_DB_HOST", "localhost")
VECTOR_DB_PORT=os.getenv("VECTOR_DB_PORT", "8000")
VECTOR_DB_COLLECTION= os.getenv("VECTOR_DB_COLLECTION", "user_input_docs")