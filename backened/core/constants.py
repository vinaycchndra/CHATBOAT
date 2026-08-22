import os 
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()

MY_SECRET = os.getenv("MY_SECRET")
TOEKN_VALIDITY  = int(os.getenv("TOKEN_VALIDITY", 3600))
LOCAL_FILE_STORAGE = Path(__file__).parent.parent / "upload_folder"
FILE_UPLOAD_CHUNK_SIZE = 1 * 1024 * 1024  # 1 MB