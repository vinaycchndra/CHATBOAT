from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import List, Optional
import logging 

logger  = logging.getLogger(__name__)

class LLMWrapper: 
    _instance = None 

    @classmethod
    def __getLLM(cls): 
        if cls._instance is None: 
            cls._instance = ChatGoogleGenerativeAI(
                                model="gemini-3.6-flash",
                                temperature=1.0,
                                max_tokens=None,
                                timeout=None,
                                max_retries=2,
                            )
        return  cls._instance   

    @classmethod
    async def sendMessageToLLM(cls, userQuestion: str, context: str, chatSummary:Optional[str], lastNChats: Optional[List[tuple[str]]]) -> str: 
        """
            userQuestion: str -> Question asked by user.
            context: str -> '\n' separated context fetched from vector db
            chatSummary: str -> So far whatever conversation summary
            lastNChats: str ->  Recent chat interaction
                
            example: 
                userQuestion = "Can you tell me about the president of India ?"
                context = "President of India is the supreme commander of Indian armed forces.\nCurrently Droupadi Murmu is the President of India."
                chatSummary = "User is asking the ai agent for the icecream making."
                lastNchats = [ 
                        ("human", "Hi!"),
                        ("ai", "How can I assist you today?"),
                        ("human", "Can you make me an ice cream ?"),
                        ("ai", "No."),
                    ]
        """

        systemMessageStr = """ You are a helpful assistant. Use the following pieces of context to answer the user's question.
                                    If you don't know the answer, just say that you don't know—do not try to make up an answer.

                                    Context:
                                    {context} 
                        """

        systemMessage = ("system", systemMessageStr)
        message_inputs = {"context": context, "userQuestion": userQuestion}

        if chatSummary: 
            systemMessageStr = systemMessageStr + """\nSummary of conversation so far: \n{chatSummary}"""
            systemMessage = ("system", systemMessageStr)
            message_inputs["chatSummary"] = chatSummary

        # initialising the message sequence
        messages = [systemMessage]

        if lastNChats: 
            messages.append(MessagesPlaceholder(variable_name="lastNChats"))
            message_inputs["lastNChats"] = lastNChats

        messages.append(("human", "{userQuestion}"))    
        prompt = ChatPromptTemplate.from_messages(messages)

        try: 
            res =  await prompt.ainvoke(message_inputs)
        except Exception as e: 
            logger.exception(e)
            raise Exception("Prompt could not be created.")

        try: 
            llm = cls.__getLLM()
        except Exception as e: 
            logger.exception(e)
            raise Exception("Could not initialise the llm.")

        try: 
            ai_response = await llm.ainvoke(res)
        except Exception as e: 
            logger.exception(e)
            raise Exception("Something happend while calling to the llm")

        return ai_response.content