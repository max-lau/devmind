import os
import time
import json
import re
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from app.logger import logger

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)

def call_llm(system_prompt: str, user_message: str) -> str:
    start = time.time()
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{{input}}")
    ], template_format="jinja2")
    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({"input": user_message})
    duration = round((time.time() - start) * 1000)
    logger.info(f"LLM call completed | model=gpt-4o-mini | duration={duration}ms | chars_in={len(user_message)} | chars_out={len(result)}")
    return result

def call_llm_json(system_prompt: str, user_message: str) -> dict:
    start = time.time()
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{{input}}")
    ], template_format="jinja2")
    chain = prompt | llm | StrOutputParser()
    raw = chain.invoke({"input": user_message})
    duration = round((time.time() - start) * 1000)
    logger.info(f"LLM JSON call completed | model=gpt-4o-mini | duration={duration}ms | chars_in={len(user_message)}")
    # Strip markdown fences if present
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Replace any unescaped double quotes inside string values with single quotes
        raw = re.sub(r'(?<=[^\\])"(?=[^,\}\]\{:]+[^\\]")', "'", raw)
        return json.loads(raw)