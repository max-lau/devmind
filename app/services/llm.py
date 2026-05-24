import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

def call_llm(system_prompt: str, user_message: str, temperature: float = 0.1) -> str:
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_message}
            ],
            "temperature": temperature
        }
    )
    return response.json()["choices"][0]["message"]["content"]


def call_llm_json(system_prompt: str, user_message: str) -> dict:
    raw = call_llm(system_prompt, user_message, temperature=0.1)
    return json.loads(raw)