import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.1,
    api_key=os.getenv("OPENAI_API_KEY")
)

def call_llm(system_prompt: str, user_message: str) -> str:
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{{input}}")
    ], template_format="jinja2")
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"input": user_message})


def call_llm_json(system_prompt: str, user_message: str) -> dict:
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{{input}}")
    ], template_format="jinja2")
    chain = prompt | llm | JsonOutputParser()
    return chain.invoke({"input": user_message})