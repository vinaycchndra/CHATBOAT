from typing import Dict, TypedDict, Annotated, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from agent.tools.utility_tools import GetRequest, GetCurrentTime
from agent.contants import WEB_SEARCH_LLM_MODEL
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import SystemMessage, HumanMessage


class WebSearchAgent:
    __instance = None

    class State(TypedDict):
        messages: Annotated[List[BaseMessage], add_messages] # this reducer maintains the messages in the state

    @classmethod
    async def __LLMNode(cls, state: State) -> Dict[str, List[BaseMessage]]:
            return {"messages": await cls.__instance.llm_model.ainvoke(state["messages"])}
        
    async def web_search(self, user_query: str) -> str:
        response = await self.__app.ainvoke({"messages": [
                    SystemMessage(content=self.__system_prompt),
                    HumanMessage(content=user_query)
                ]
            })
        
        final_response = [message_object.get("text") for message_object in response['messages'][-1].content if message_object.get("type") == "text"]    
        return "\n".join(final_response)

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls.__instance = WebSearchAgent()
            cls.__instance.llm_model = ChatGoogleGenerativeAI(
                                                        model=WEB_SEARCH_LLM_MODEL,
                                                        temperature=0.7,
                                                        max_retries=2
                                                    )
            # defining tools
            cls.__instance.__tools = [GetRequest, GetCurrentTime]
            cls.__instance.llm_model = cls.__instance.llm_model.bind_tools(cls.__instance.__tools)

            # adding nodes to the graph    
            graph_builder = StateGraph(cls.State)
            graph_builder.add_node("llm_node", cls.__LLMNode)
            graph_builder.add_node("web_search_node", ToolNode(tools = cls.__instance.__tools))

            # add  edges to the graph or the flow logic 
            graph_builder.add_edge(START, "llm_node")
            graph_builder.add_conditional_edges("llm_node", tools_condition, path_map={"tools": "web_search_node", "__end__": END})
            graph_builder.add_edge("web_search_node", "llm_node")

            # compiling the graph
            cls.__instance.__app = graph_builder.compile()
            cls.__instance.__system_prompt = (
                    "You are a helpful assistant."
                    "If you know the answer with high confidence, answer directly. "
                    "If you do not know the answer or require recent/real-time context, you MUST call the `web_search` / `get_current_time` tool to make informed responses."
            )

        return cls.__instance