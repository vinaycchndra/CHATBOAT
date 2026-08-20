import bcrypt
from dataAccessLayer.userDal import UserOdmLayer 
from core.exceptions import UserAlreadyExistsException, EntityDoesNotExist, InvalidInputError
from core.auth_utils import JwtUtil
from typing import Dict

class UserService: 

    @staticmethod
    async def register_user(name: str, password: str, email: str) -> Dict: 
        # Check if the mail already exists 
        user_object = await UserOdmLayer.get_user(email=email)

        if user_object: 
            raise UserAlreadyExistsException(email=email)

        # Encoding is actually converting the strings to the bytes.
        hashed_password_bytes = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        # Hashed password string.
        hashed_password = hashed_password_bytes.decode()

        # Creating the user.
        created_user = await UserOdmLayer.create_user(name = name, hashed_password=hashed_password, email=email)

        return {"user_id": str(created_user.id), "email": created_user.email}

    @staticmethod
    async def login_user(email: str, password: str) -> Dict: 
        user_object = await UserOdmLayer.get_user(email=email)

        # check user exists
        if not user_object: 
            raise EntityDoesNotExist(f"User with {email} does not exist.")

        # match password
        if not bcrypt.checkpw(password=password.encode(), hashed_password=user_object.password.encode()): 
            raise InvalidInputError("Password does not match.")

        # create new token
        token = JwtUtil.get_token(user_id=str(user_object.id), email = user_object.email, is_active = True)

        # update token in cache TODO

        return  {"token": token, "user_id": str(user_object.id)}






        

