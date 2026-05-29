import os
import time
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
    chain = prompt | llm | JsonOutputParser()
    result = chain.invoke({"input": user_message})
    duration = round((time.time() - start) * 1000)
    logger.info(f"LLM JSON call completed | model=gpt-4o-mini | duration={duration}ms | chars_in={len(user_message)}")
    return result