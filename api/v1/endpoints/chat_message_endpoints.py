from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from services.EmbeddingService import VectorEmbeddingService
from api.v1.schemas.models import MessageModel
from core.middleware import AuthMiddleware
from services.chat_service import ChatMessageService, ChatSessionService
from services.LLMs_service import GeminiLLM

chat_message_router = APIRouter(
    prefix="/v1/chat-message",
    dependencies=[Depends(AuthMiddleware.authenticate)],
    tags=["chat_message"],
    responses={404: {"description": "Not found"}},
)

@chat_message_router.post("/{session_id}/send", tags=["send_message"])
async def create_session(request: Request, payload: MessageModel, session_id: str): 
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
            # call the back ground summarisation
            pass 

        # input the ai model and get the response 
        ai_response = await GeminiLLM.sendMessageToLLM(userQuestion=human_message, context=input_context, chatSummary=session_summary, lastNChats=previous_messages_list)

        # save the user question into the db
        await ChatMessageService.create_messasge(session_id=session_id, role="human", message_text=human_message)

        # save model reponse into the db
        saved_ai_message = await ChatMessageService.create_messasge(session_id=session_id, role="ai", message_text=ai_response)

        return_payload = {
            "role": saved_ai_message.get("role"), 
            "message": saved_ai_message.get("message")
        }
    except Exception as e: 
        return JSONResponse(status_code=500, content={"message": str(e)})
    
    return JSONResponse(status_code=201, content = return_payload)
    




    
    