import asyncio
import logging
from functools import wraps

logger = logging.getLogger(__name__)

# asynchronous decorator
def retry(attempts: int = 3, wait: int = 5):
    def function_consumer(func):
        @wraps(func)
        async def input_consumer(*args, **kwargs):
            attempt = 1
            while attempt <= attempts: 
                try: 
                    res = await func(*args, **kwargs)
                    return res
                except Exception: 
                    if attempt == attempts:
                        raise
                    logger.info(f"Failed while executing the function for {attempt} time,  will wait for {wait} seconds")
                await asyncio.sleep(wait)
                attempt += 1
        return input_consumer
    return function_consumer