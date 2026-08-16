import logging
from models.user import User
from beanie import PydanticObjectId

logger = logging.getLogger(__name__)

class UserOdmLayer: 

    @staticmethod
    async def create_user(name: str, hashed_password: str, email: str) -> User: 
        try:
            userObject = User(name=name, password=hashed_password, email=email)
            await userObject.insert()
        except Exception as e: 
            logger.exception("Something happend while inserting the user in the db...")
            raise e
        return userObject

    @staticmethod
    async def get_user(email: str = None, user_id: str = None) -> User: 
        if email is None and user_id is None: 
            raise Exception("Atleast one field email or user_id is required to fetch the user.")

        if email: 
            user_obj = await User.find_one({"email": email})
        elif user_id: 
            user_obj = await User.find_one({"_id": PydanticObjectId(user_id)})

        return user_obj
                        