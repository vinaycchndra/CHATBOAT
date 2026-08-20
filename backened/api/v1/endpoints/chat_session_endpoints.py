from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from services.chat_service import ChatSessionService 
from api.v1.schemas.models import ChatSessionModel
from core.exceptions import EntityDoesNotExist, UnAuthorizedAccess
from core.middleware import AuthMiddleware

chat_session_router = APIRouter(
    prefix="/v1/chat-session",
    dependencies=[Depends(AuthMiddleware.authenticate)],
    tags=["chat_session"],
    responses={404: {"description": "Not found"}},
)

@chat_session_router.post("/create", tags=["create_session"])
async def create_session(request: Request): 
    user_email = request.state.user_email
    try:
        payload = await ChatSessionService.create_chat_session(email=user_email)
    except EntityDoesNotExist: 
        return JSONResponse(status_code=400, content = {"message": "User does not exist."})
    except  Exception as e: 
        return JSONResponse(status_code=400, content = {"message": str(e)})

    return JSONResponse(status_code=201, content=payload)


@chat_session_router.get("/get-session/{session_id}", tags=["get_session"])
async def get_session(session_id: str, request: Request): 
    user_id = request.state.user_id
    try:
        payload = await ChatSessionService.get_chat_session(session_id=session_id, user_id=user_id)
    except UnAuthorizedAccess: 
        return JSONResponse(status_code=401, content = {"message": "User does not have this chat session"})
    except  Exception as e: 
        return JSONResponse(status_code=400, content = {"message": str(e)})

    return JSONResponse(status_code=200, content=payload)


@chat_session_router.post("/archive-session/{session_id}", tags=["archive_session"])
async def archive_session(session_id: str, request: Request): 
    user_id = request.state.user_id
    try:
        payload = await ChatSessionService.update_chat_session(session_id=session_id, user_id=user_id, archive=True)
    except UnAuthorizedAccess: 
        return JSONResponse(status_code=401, content = {"message": "User does not have this chat session"})
    except  Exception as e: 
        return JSONResponse(status_code=400, content = {"message": str(e)})

    return JSONResponse(status_code=201, content=payload)


@chat_session_router.post("/session-summary/{session_id}", tags=["archive_session"])
async def update_session_summary(session_id: str, request: Request, payload: ChatSessionModel): 
    user_id = request.state.user_id
    session_summary = payload.session_summary

    if not session_summary: 
        return JSONResponse(status_code=400, content={"message": "session summary is empty."})
    
    try:
        payload = await ChatSessionService.update_chat_session(session_id=session_id, user_id=user_id, session_summary=session_summary)
    except UnAuthorizedAccess: 
        return JSONResponse(status_code=401, content = {"message": "User does not have this chat session"})
    except  Exception as e: 
        return JSONResponse(status_code=400, content = {"message": str(e)})

    return JSONResponse(status_code=201, content=payload)


@chat_session_router.post("/query-session/", tags=["query_session"])
async def query_session(payload: ChatSessionModel, request: Request): 
    query = {"user_id": request.state.user_id}

    if payload.session_ids: 
        query["session_ids"] = payload.session_ids

    if payload.created_at: 
        query["created_at"] = payload.created_at 

    if payload.updated_at: 
        query["updated_at"] = payload.updated_at 

    if payload.archived is not None: 
        query["archived"] = payload.archived

    try:
        res = await ChatSessionService.query_chat_sessions(**query)
    except Exception as e: 
        return JSONResponse(status_code=400, content = {"message": str(e)})

    return JSONResponse(status_code=200, content={"data": res})
    

    