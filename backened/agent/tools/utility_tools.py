from urllib.parse import urlencode
from langchain_core.tools import tool
from typing import List, Dict
from agent.utils.search_api_client import WebSearchClient
from agent.utils.decorators import retry
from agent.contants import SERPER_API_KEYS
from datetime import datetime

# GetRequest tool for web search
@tool(
    "web_search", 
    description="Searches the web for real-time information and returns search titles and  text snippets from the internet."
)
@retry(attempts=3,wait=5)
async def GetRequest(query: str) -> List[Dict[str, str]]: 
    query_params = {"q": query, "apiKey": SERPER_API_KEYS}
    query_string = urlencode(query_params)
    url = f"https://google.serper.dev/search?{query_string}"
    try: 
        response_dict = await WebSearchClient.Get(url=url)
    except Exception as e: 
        return [{"error": str(e)}]
    
    res_list = response_dict.get("organic", [])
    res = [{"title": json_.get("title", ""), "text": json_.get("snippet", "")} for json_ in res_list if json_.get("snippet") and json_.get("title")]
    return res


# Get current time tool.
@tool(
    "get_current_time", 
    description="Gives the current time in UTC format."
)
async def GetCurrentTime() -> str:
    """Returns the current time in UTC format."""
    return datetime.utcnow().isoformat() + "Z"