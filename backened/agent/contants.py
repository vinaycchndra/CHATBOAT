import os
from dotenv import load_dotenv


load_dotenv()

SERPER_API_KEYS = os.getenv("SERPER_API_KEYS")
WEB_SEARCH_LLM_MODEL = "gemini-3.5-flash-lite"