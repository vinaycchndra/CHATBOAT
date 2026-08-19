from fastapi import FastAPI, APIRouter, Request, Depends
from core.middleware import AuthMiddleware
from api.v1.endpoints.users_endpoints import user_router
from api.v1.endpoints.chat_session_endpoints import chat_session_router
from api.v1.endpoints.chat_message_endpoints import chat_message_router
from dotenv import load_dotenv
from db.mongodb import initDb
from services.EmbeddingService import VectorEmbeddingService

app = FastAPI()
app.include_router(user_router)
app.include_router(chat_session_router)
app.include_router(chat_message_router)

@app.on_event("startup")
async def startup_event():
    # await VectorEmbeddingService.createEmbeddingForFile(fileType="application/pdf", filePath="/home/vishal/Desktop/ChatBoat/data/Medical_book.pdf", userId="6a82b8324124d6a72005d3e2", documentId="my_document")
    load_dotenv()
    await initDb()
        
    






















































# import asyncio
# # from services import EmbeddingService, LLMs_service
# from db.mongodb import initDb
# from dotenv import load_dotenv
# from models.user import User
# # from models.chatModels import ChatSession, ChatMessage, ChatRoles
# async def main():
#     load_dotenv()
#     await initDb()
    
#     user = await User.find_one({"email" :"ashok@mail.com"})

#     print(user)

#     # obj = ChatSession(session_summary="so far story is the name...", userId = user)
#     # obj_updated = await obj.save()

#     # if obj is obj_updated:
#         # print("same...")

#     # print(obj_updated)

#     # obj = ChatMessage(sessionId=obj_updated, role = ChatRoles.HUMAN, messageText= "Hi ai how are you ? ")
#     # await obj.save()


#     # await EmbeddingService.VectorEmbeddingService.createEmbeddingForFile(fileType="application/pdf", filePath="./data/Medical_book.pdf", userId=1, documentId=1)
#     # data = await EmbeddingService.VectorEmbeddingService.QueryVectorDb(user_id=1, text = "what is this sebaceous glands ?", top_n=10)
#     # for data_ in data: 
#     #     print(data_, "\n\n\n")
# #     userQuestion = "what is a keloids ? "
# #     context = """A keloid is an overgrown, raised scar that expands beyond the boundaries of the original skin injury.

# # Unlike typical scars—which flatten and fade over time—keloids happen when the body’s healing process goes into overdrive, producing excess collagen (the protein that forms the structure of skin).

# # Key Characteristics & Symptoms
# # Appearance: Raised, thick, firm, and often rubbery or shiny. They can range in color from pink or red to dark brown.

# # Growth Pattern: They grow continuously over months or years, spreading beyond the borders of the initial wound.

# # Sensations: Often accompanied by itching, tenderness, or sharp/burning discomfort, especially while actively growing.

# # Common Locations: Chest, back, shoulders, ears (from piercings), and jawline—areas where the skin experiences high tension or frequent movement.

# # Causes and Triggers
# # Keloids can develop after almost any type of skin trauma, including:

# # Surgical incisions or wounds

# # Ear or body piercings

# # Acne, chickenpox, or bug bite scars

# # Tattoos

# # Minor burns, scratches, or abrasions"""
# #     chatSummary = "User is asking the ai agent for the icecream making."
# #     lastNchats = [ 
# #                             ("human", "Hi!"),
# #                             ("ai", "How can I assist you today?"),
# #                             ("human", "Can you make me an ice cream ?"),
# #                             ("ai", "No."),
# #                         ]
# #     response = await LLMs_service.GeminiLLM.sendMessageToLLM(userQuestion=userQuestion, chatSummary=chatSummary, lastNChats=lastNchats, context=context)
# #     print(response)

# #     response = await LLMs_service.GeminiLLM.summariseWithExistingSummary(existingSummary="So far human and ai are interacting on a abnormal scar tissue called Keloids.",
# #                                 lastNChats= [("human", "can you tell how many types of these keloids are there ? "),
# #                                         ("ai", "Fresh Nodular Keloids, Superficial Spreading (Butterfly) Keloids, Mature ('Burned-Out') Keloids are some of the keloids."),
# #                                         ("human", "can you tell me how to make burger ?"), 
# #                                         ("ai", "I don't know about that.")
# #                                 ])
# #     print(response)
# asyncio.run(main())
