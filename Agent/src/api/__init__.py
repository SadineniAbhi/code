import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pymongo import AsyncMongoClient
from pydantic import BaseModel
import src.api.routes as routes
from langgraph.checkpoint.mongodb.aio import AsyncMongoDBSaver
from langgraph.checkpoint.memory import MemorySaver
from src.agent.graph import build_workflow
from dotenv import load_dotenv
from src.api.utilis import get_tools, get_llm_with_tools

class MessageRequest(BaseModel):
    query: str
    threadID: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()
    try:
        # MongoDB persistent memory (commented out - using in-memory instead)
        # conn_string = os.environ.get('conn_string')
        # db_name = os.environ.get('db_name')
        # if conn_string is None or db_name is None:
        #     raise ValueError("Connection string and db_name must be set")
        # client = AsyncMongoClient(
        #     conn_string
        # )
        # checkpointer = AsyncMongoDBSaver(client, db_name=db_name)
        # await checkpointer._setup()

        # Using in-memory checkpointer
        checkpointer = MemorySaver()

        tools = await get_tools()
        llm_with_tools = get_llm_with_tools(tools)
        workflow = build_workflow(tools, llm_with_tools)
        graph = workflow.compile(checkpointer=checkpointer)

        app.state.graph = graph
        # app.state.mongo_client = client 
        yield  

    except Exception as e:
        logging.error(f"Error initializing LangGraph: {e}")
        raise

    # finally:
    #     app.state.mongo_client.close()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify ["http://localhost:3000"] for more security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(routes.router)