import os 
from dotenv import load_dotenv

load_dotenv()

MY_SECRET = os.getenv("MY_SECRET")
TOEKN_VALIDITY  = int(os.getenv("TOKEN_VALIDITY", 3600))