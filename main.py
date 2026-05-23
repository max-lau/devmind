import os
import json
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

app = FastAPI(
    title="DevMind API",
    description="AI-powered developer productivity tools",
    version="0.1.0"
)

SYSTEM_PROMPT = """
You are a bug triage assistant for a software engineering team.

When given a GitHub issue title, respond with ONLY a JSON object. No explanation, no markdown, no code fences. Raw JSON only.

The JSON must have exactly these fields:
{
  "severity": "critical" | "high" | "medium" | "low",
  "category": "bug" | "performance" | "security" | "feature" | "docs",
  "summary": "one sentence description of the issue",
  "suggested_owner": "frontend" | "backend" | "devops" | "unknown",
  "needs_immediate_attention": true | false
}

Examples:

Issue: "500 error on checkout page"
{"severity":"critical","category":"bug","summary":"The checkout page returns a 500 server error, blocking purchases.","suggested_owner":"backend","needs_immediate_attention":true}

Issue: "update README installation steps"
{"severity":"low","category":"docs","summary":"The README installation instructions need to be updated.","suggested_owner":"unknown","needs_immediate_attention":false}
"""

# --- Request and Response models ---

class IssueRequest(BaseModel):
    title: str

class IssueResponse(BaseModel):
    severity: str
    category: str
    summary: str
    suggested_owner: str
    needs_immediate_attention: bool

# --- Routes ---

@app.get("/")
def root():
    return {"status": "DevMind API is running"}

@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}

@app.post("/analyze-issue", response_model=IssueResponse)
def analyze_issue(request: IssueRequest):
    if not request.title.strip():
        raise HTTPException(status_code=400, detail="Issue title cannot be empty")

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Issue title: {request.title}"}
            ],
            "temperature": 0.1
        }
    )

    raw = response.json()["choices"][0]["message"]["content"]

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Model returned invalid JSON")

    return result
