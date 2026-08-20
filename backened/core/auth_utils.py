import jwt
from datetime import datetime, timezone, timedelta
from core.exceptions import InvalidInputError
from core.constants import MY_SECRET, TOEKN_VALIDITY
from typing import Dict

class JwtUtil: 

    @staticmethod
    def get_token(user_id: str, email: str, is_active: bool = True, is_admin: bool = False) -> str: 

        if not user_id or not email: 
            raise InvalidInputError("User id and email is required.")

        expiry_time = datetime.now(timezone.utc)+timedelta(seconds=TOEKN_VALIDITY)

        payload = {
            "user_id": user_id, 
            "email": email,
            "is_active": is_active, 
            "is_admin": is_admin, 
            "validity": expiry_time.isoformat()
        }
        token = jwt.encode(payload=payload, key=MY_SECRET, algorithm='HS256')
        return token 

    @staticmethod
    def parse_token(token: str) -> Dict:
        payload = jwt.decode(token, key=MY_SECRET, algorithms=['HS256',])
        return payload  



        

