from fastapi import Request, HTTPException
from core.auth_utils import JwtUtil
from  dateutil import parser
from datetime import datetime, timezone 


class AuthMiddleware:

    @staticmethod
    async def authenticate(request: Request):
        invalid_token_exception = HTTPException(status_code=400, detail="Invalid Token")
        
        bearer_token = request.headers.get("Authorization")
        
        if not bearer_token:
            raise invalid_token_exception

        if not bearer_token.startswith("Bearer "):
            raise invalid_token_exception
        
        split_token = bearer_token.split(" ")

        if len(split_token) <= 1:
            raise invalid_token_exception

        token = split_token[1]
        payload = JwtUtil.parse_token(token)
        expiry_datetime = parser.parse(payload.get("validity"), tzinfos={"tzname": "UTC"})

        if datetime.now(timezone.utc) >  expiry_datetime:     
            raise HTTPException(
                status_code=403, 
                detail="Token expired."
            )

        request.state.user_email = payload.get("email")
        request.state.user_id = payload.get("user_id")
    





















