import os
import json
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


def get_default_prompt_template_path(): # add this to the .env file
    prompt_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'prompt.md')
    return prompt_path

def get_prompt_template() -> ChatPromptTemplate:
    prompt_path = os.environ.get("PROMPT_PATH", get_default_prompt_template_path())
    with open(prompt_path, "r", encoding="utf-8") as file:
        instructions_text = file.read()
    
    return ChatPromptTemplate.from_messages([
        ("system", instructions_text),
        MessagesPlaceholder(variable_name="messages"),
    ])