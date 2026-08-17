from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from services.userService import UserService 
from api.v1.schemas.models import UserLogin, UserRegister
from core.exceptions import EntityDoesNotExist, InvalidInputError

user_router = APIRouter(
    prefix="/v1/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

@user_router.post("/login/", tags=["login"])
async def login_user(payload: UserLogin, request: Request): 
    try:
        user_detail = await UserService.login_user(email=payload.email, password=payload.password)
    except EntityDoesNotExist: 
        return JSONResponse(status_code=400, content={"message": f"User: {payload.email} does not exist"})
    except InvalidInputError as e: 
        return JSONResponse(status_code=400, content={"message": str(e)})
    return JSONResponse(status_code=201, content=user_detail)


@user_router.post("/register/", tags=["register"])
async def login_user(payload: UserRegister): 
    try:
        user_detail = await UserService.register_user(name=payload.name, email=payload.email, password=payload.password)
    except Exception as e: 
        return JSONResponse(status_code=400, content={"message": str(e)})
    return JSONResponse(status_code=201, content=user_detail)




