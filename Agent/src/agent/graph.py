from typing import Any, Dict
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.prebuilt import ToolNode
from .nodes import chat, route_chat_node

def build_workflow(tools: list[Any], llm_with_tools: Any) -> StateGraph:
    workflow = StateGraph(MessagesState)
    async def chat_node(state: Dict[str, Any]) -> Dict[str, Any]:
        return await chat(llm_with_tools, state)
    workflow.add_node("chat", chat_node)
    workflow.add_node("tools", ToolNode(tools))
    workflow.add_edge(START, "chat")
    workflow.add_conditional_edges("chat", route_chat_node)
    workflow.add_edge("tools", "chat")
    workflow.add_edge("chat", END)
    return workflow

