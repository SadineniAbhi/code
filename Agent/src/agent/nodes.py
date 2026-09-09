from typing import Any, Dict
from langchain_core.messages.utils import trim_messages, count_tokens_approximately
from langchain_core.messages import AIMessage
from langgraph.graph import END
from .utilis import get_prompt_template
import logging


async def chat(llm_with_tools: Any, state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        trimmed_messages = trim_messages(
            state["messages"],
            strategy="last",
            token_counter=count_tokens_approximately,
            max_tokens=80000,
            start_on="human",
            end_on=("human", "tool"),
        )
        prompt_template = get_prompt_template()
        prompt = prompt_template.invoke({"messages": trimmed_messages})
        response = await llm_with_tools.ainvoke(prompt)
        return {"messages": [response]}
    except Exception as e:
        logging.error(f"Error during chat processing: {e}")
        return {"messages": [AIMessage(content=f"Sorry, an error occurred: {e}")]}  

async def route_chat_node(state: Dict[str, Any]) -> str:
    last_message = state["messages"][-1]
    tool_calls = getattr(last_message, "additional_kwargs", {}).get("tool_calls", [])
    return "tools" if tool_calls else END
