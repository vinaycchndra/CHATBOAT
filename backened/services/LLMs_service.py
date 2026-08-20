from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import List, Optional
import logging 

logger  = logging.getLogger(__name__)

class GeminiLLM: 
    _instance = None 

    @classmethod
    def __getLLM(cls): 
        if cls._instance is None: 
            cls._instance = ChatGoogleGenerativeAI(
                model="gemini-3.5-flash-lite",  # Ultra-fast and lightweight
                temperature=0.7,
                max_retries=2
            )
        return  cls._instance   

    @classmethod
    async def sendMessageToLLM(cls, userQuestion: str, context: str, chatSummary:Optional[str], lastNChats: Optional[List[tuple[str, str]]]) -> str: 
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
                                    Please give stuctured answers with new line tags so that can be rendered properly.

                                    Context:
                                    {context} 
                        """

        systemMessage = ("system", systemMessageStr)
        message_inputs = {"context": context, "userQuestion": userQuestion}

        if chatSummary and False: 
            systemMessageStr = systemMessageStr + """\nSummary of conversation so far: \n{chatSummary}"""
            systemMessage = ("system", systemMessageStr)
            message_inputs["chatSummary"] = chatSummary

        # initialising the message sequence
        messages = [systemMessage]

        if lastNChats and False: 
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

        return ai_response.content[0]["text"]


    @classmethod
    async def summariseWithExistingSummary(cls, existingSummary: Optional[str], lastNChats: Optional[List[tuple[str, str]]]) -> str: 
        """
            existingSummary: str -> So far human and ai are interacting on a abnormal scar tissue called Keloids.
            lastNChats: str ->  Recent chat interaction ex: [
                                                                ("human", "can you tell me about the keloids ?"), 
                                                                ("ai", "Unlike typical scars, which flatten and fade over time, keloids grow continuously over months or years and spread beyond the initial wound.")
                                                            ]
                
            """
        if (lastNChats is None or not lastNChats):
            raise Exception("last N chats can not be empty...")

        # initialising the set of messages and variables.
        template_input =  {"lastNChats": "\n".join([f"{role}: {text}" for role, text in lastNChats])}

        # Initialising the system prompt.
        if existingSummary is None or existingSummary == "": 
            promptTemplate = """You are ai assistant who summarises the sequence of chat into an overall discussion summary between the ai agent and a human.  Please summarise under 200 words. Here is conversation between human and ai\n{lastNChats}."""
        else:
            promptTemplate = """You are ai assistant who updated the existing conversation summary with the existing chat sequence between ai and human. Please summarise under 200 words. Here is existing summary:\n {previousSummary} and current sequence of chat between the ai agent and a human is \n{lastNChats}"""
            template_input["previousSummary"] = existingSummary

        # # create the overall prompt 
        prompt = ChatPromptTemplate.from_template(promptTemplate)

        # call the LLM to summarise
        try: 
            res =  await prompt.ainvoke(template_input)
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

        return ai_response.content[0]["text"]
        
             