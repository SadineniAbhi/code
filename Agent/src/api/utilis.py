import os
import json
from fastapi import Request
from src.api.schemas import MessageRequest
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv
from langfuse.langchain import CallbackHandler
from dotenv import load_dotenv
load_dotenv()

def get_graph(request: Request):
    graph = request.app.state.graph
    return graph

def process_input(data: MessageRequest) -> dict[str, list[HumanMessage]]:
    input = {"messages": [HumanMessage(content=data.query)]}
    return input

def get_config(data: MessageRequest) -> dict[str, dict[str, str]]:
    langfuse_handler = CallbackHandler()
    config = {"configurable": {"thread_id": data.threadID}, "callback": [langfuse_handler] }
    return config

async def event_stream(graph, input: dict[str, list[HumanMessage]], config: dict[str, dict[str, str]]):
    try:
        async for event in graph.astream_events(input, config):
            if (
                event["event"] == "on_chat_model_stream"
                and event["metadata"].get("langgraph_node") == "chat"
            ):
                yield event["data"]["chunk"].content
    except Exception as e:
        yield f"Error: {str(e)}"

def check_and_load_env():
    REQUIRED_ENV_VARS = [
    'OPENAI_API_KEY',
    # 'AZURE_OPENAI_ENDPOINT',  # For Azure OpenAI
    # 'AZURE_OPENAI_API_KEY',    # For Azure OpenAI
    # 'conn_string',             # For MongoDB persistent memory
    # 'db_name',                 # For MongoDB persistent memory
    'MCP_SERVERS_JSON',
    # 'SPACE_ID'                 # Optional
    ]
    missing_vars = [var for var in REQUIRED_ENV_VARS if not os.environ.get(var)]
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

# def get_ttl_config() -> dict[str, int|str]:
#     default_ttl = os.getenv("REDIS_TTL_DEFAULT")
#     refresh_on_read = os.getenv("REDIS_TTL_REFRESH_ON_READ")

#     if default_ttl is not None and refresh_on_read is not None:
#         return {
#             "default_ttl": int(default_ttl),
#             "refresh_on_read": refresh_on_read.lower()
#         }
#     raise ValueError  


def load_config():
    """Load the configuration from environment variable or fallback to default path."""
    json_string = os.environ.get("MCP_SERVERS_JSON")
    if json_string is None:
        raise ValueError("config path can not be None")
    return json.loads(json_string)

async def get_tools():
    """
    Load all MCP server configs from mcp.json and initialize tools.
    Returns a list of tools: [TavilySearch, ...MCP tools]
    """
    config = load_config()
    mcp_client = MultiServerMCPClient(config)
    mcp_tools = await mcp_client.get_tools()
    return mcp_tools

def get_llm_with_tools(tools):
    load_dotenv()
    """Bind tools to the OpenAI LLM using the model from environment variable."""
    
    # Azure OpenAI (commented out - using regular OpenAI instead)
    # model = AzureChatOpenAI(    
    #     azure_deployment="gpt-4.1",  
    #     api_version="2025-01-01-preview",
    #     max_tokens=None,
    #     timeout=None,
    #     max_retries=2,
    # )
    
    # Using regular OpenAI
    model = ChatOpenAI(
        model="gpt-4o",  # or "gpt-4-turbo", "gpt-3.5-turbo"
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )
    
    return model.bind_tools(tools, parallel_tool_calls=False)