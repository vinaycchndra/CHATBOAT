import httpx
import logging

logger = logging.getLogger(__name__)

class WebSearchClient:
    @classmethod 
    async def Get(cls, url: str, headers: dict = {}) -> dict: 
        """This is the get api client method"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
        except Exception: 
            logger.exception(f"Something happened making call : {url}")
            raise 

        if response.status_code == 200: 
            return response.json()
        else: 
            raise Exception(response.text)