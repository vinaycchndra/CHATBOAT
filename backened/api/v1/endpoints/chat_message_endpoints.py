from urllib import request

from fastapi import APIRouter, Request, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from services.EmbeddingService import VectorEmbeddingService
from api.v1.schemas.models import MessageModel, WebSearchModel
from core.middleware import AuthMiddleware
from services.chat_service import ChatMessageService, ChatSessionService
from services.LLMs_service import GeminiLLM
from core.exceptions import UnAuthorizedAccess
from agent.agents.web_search_agent import WebSearchAgent
from models.Models import ChatRoles

chat_message_router = APIRouter(
    prefix="/v1/chat-message",
    dependencies=[Depends(AuthMiddleware.authenticate)],
    tags=["chat_message"],
    responses={404: {"description": "Not found"}},
)

@chat_message_router.post("/{session_id}/send", tags=["send_message"])
async def create_response(request: Request, payload: MessageModel, session_id: str, background_tasks: BackgroundTasks): 
    try: 
        user_id = request.state.user_id

        # get the message by the human 
        human_message = payload.message_text
        contexts = await VectorEmbeddingService.QueryVectorDb(user_id = user_id, text = human_message, top_n = 20)
        
        prepared_context = []
        for context in contexts: 
            prepared_context.append(context.get("text"))

        if len(prepared_context) > 0: 
            input_context = "\n".join(prepared_context)
        else: 
            input_context = ""

        # get the session summary from the db 
        session_object = await ChatSessionService.get_chat_session(session_id=session_id, user_id=user_id)
        session_summary = session_object.get("session_summary")
        
        # get the non-summarized messages to be feed as input to the LLM. 
        previous_messages = await ChatMessageService.query_message(session_id=session_id, is_summarized=False)
        previous_messages_list = []
        for previous_message in previous_messages: 
            previous_messages_list.append((previous_message.get("role"), previous_message.get("message"))) 

        # check their count if more than the specified call the summarisation background process.
        if len(previous_messages) > 5: 
            background_tasks.add_task(ChatMessageService.summarize_messages, session_id, user_id)

        # input the ai model and get the response 
        ai_response = await GeminiLLM.sendMessageToLLM(userQuestion=human_message, context=input_context, chatSummary=session_summary, lastNChats=previous_messages_list)
        
        # save the user question into the db
        saved_human_message = await ChatMessageService.create_messasge(session_id=session_id, role="human", message_text=human_message)

        # save model reponse into the db
        saved_ai_message = await ChatMessageService.create_messasge(session_id=session_id, role="ai", message_text=ai_response.get("response_text"), is_informed=ai_response.get("informed_response", False))

        return_payload = {
            "ai_message_id": str(saved_ai_message.get("message_id")),
            "role": saved_ai_message.get("role"), 
            "message": saved_ai_message.get("message"), 
            "is_informed": saved_ai_message.get("is_informed"),
            "human_message_id": str(saved_human_message.get("message_id")),
        }
    except Exception as e: 
        return JSONResponse(status_code=500, content={"message": str(e)})
    
    return JSONResponse(status_code=201, content = return_payload)
    

@chat_message_router.get("/{session_id}/messages", tags=["get_message"])
async def query_messages(request: Request, session_id: str, limit: int = 20, offset: int = 0): 
    user_id = request.state.user_id

    # permission access
    try: 
        await ChatSessionService.get_chat_session(session_id=session_id, user_id=user_id)
    except UnAuthorizedAccess: 
        return JSONResponse(status_code=400, content={"message": "You don't have access to this session messages."})

    try:
        messages = await ChatMessageService.query_message(session_id=session_id, limit=limit, offset=offset)
    except Exception as e: 
        return JSONResponse(status_code=400, content={"message": str(e)})

    return JSONResponse(status_code=200, content = messages)


@chat_message_router.put("/{session_id}/message/web_search_agent", tags=["update_response_from _web_search_agent"])
async def update_message_from_web_search_agent(request: Request, session_id: str, payload: WebSearchModel): 
    user_id = request.state.user_id
    ai_message_id = payload.ai_message_id
    human_message_id = payload.human_message_id


    # validating the ai message
    try: 
        ai_message_object = await ChatMessageService.get_message_details(session_id=session_id, message_id=ai_message_id, user_id=user_id)
    except Exception as e: 
        return JSONResponse(status_code=400, content={"message": str(e)})

    if ai_message_object.get("is_informed") or ai_message_object.get("role") != ChatRoles.AI: 
        return JSONResponse(status_code=400, content={"message": "The AI message is already informed or this message is not from the AI."})

    # Validating the human message
    try: 
        human_message_object = await ChatMessageService.get_message_details(session_id=session_id, message_id=human_message_id, user_id=user_id)
    except Exception as e: 
        return JSONResponse(status_code=400, content={"message": str(e)})

    if human_message_object.get("role") != ChatRoles.HUMAN: 
        return JSONResponse(status_code=400, content={"message": "The human message is not from the human role or this message is not from the human."})
    
    human_query = human_message_object.get("message")
    if not human_query: 
        return JSONResponse(status_code=400, content={"message": "The human message is empty. Cannot perform web search."})

    # calling the agent to perform the web search and get the response.
    web_search_agent = WebSearchAgent.get_instance()
    web_search_response = await web_search_agent.web_search(user_query=human_query)
    
    # updating the message text or the fields
    try:
        updated_message = await ChatMessageService.update_message_details(session_id = session_id, message_id = ai_message_id, user_id = user_id,  message_text = web_search_response, is_informed = True)
    except Exception as e: 
        return JSONResponse(status_code=400, content={"message": "Something happened while updating the AI message with the web search response."})
    
    return JSONResponse(status_code=201, content = updated_message)
        

