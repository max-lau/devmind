import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from app.services.llm import call_llm_json

router = APIRouter(prefix="/review", tags=["Code Review"])

INJECTION_PATTERNS = [
    "ignore previous instructions",
    "ignore all instructions",
    "disregard your",
    "you are now",
    "new instruction",
    "system prompt",
    "jailbreak",
]

def check_injection(text: str) -> None:
    lower = text.lower()
    for pattern in INJECTION_PATTERNS:
        if pattern in lower:
            raise HTTPException(status_code=400, detail="Invalid input detected")

CODE_REVIEW_PROMPT = """
You are an expert Python code reviewer working on a professional software team.
When given a Python function, respond with ONLY a JSON object. No explanation, no markdown, no code fences. Raw JSON only.
The JSON must have exactly these fields:
{
  "overall_score": <integer 1-10>,
  "issues": [
    {
      "line": <line number or null if general>,
      "severity": "critical" | "high" | "medium" | "low",
      "type": "bug" | "security" | "performance" | "style" | "maintainability",
      "description": "clear explanation of the issue",
      "suggestion": "exactly how to fix it"
    }
  ],
  "has_docstring": true | false,
  "has_type_hints": true | false,
  "summary": "one paragraph overall assessment"
}

Issue type guidance:
- "bug": logic errors, crashes, incorrect behaviour
- "security": injection, auth issues, data exposure
- "performance": N+1 queries, unnecessary loops, memory waste
- "style": naming, missing type hints, PEP8
- "maintainability": unclosed resources, missing context managers, deeply nested code, no error handling, hard-coded values

Examples:
Function:
def divide(a, b):
    return a / b
{"overall_score":4,"issues":[{"line":2,"severity":"critical","type":"bug","description":"No check for division by zero","suggestion":"Add 'if b == 0: raise ValueError(\"Cannot divide by zero\")' before the return"},{"line":1,"severity":"low","type":"style","description":"Missing type hints","suggestion":"Change signature to: def divide(a: float, b: float) -> float:"}],"has_docstring":false,"has_type_hints":false,"summary":"The function works for the happy path but will crash with a ZeroDivisionError when b is 0. Needs input validation and type hints."}

Function:
def read_config(path):
    f = open(path)
    data = f.read()
    f.close()
    return data
{"overall_score":5,"issues":[{"line":2,"severity":"high","type":"maintainability","description":"File opened manually without a context manager — if an exception occurs before f.close(), the file handle leaks","suggestion":"Use 'with open(path) as f: data = f.read()' instead"},{"line":1,"severity":"medium","type":"bug","description":"No error handling if the file does not exist","suggestion":"Wrap in try/except FileNotFoundError and raise a meaningful error"},{"line":1,"severity":"low","type":"style","description":"Missing type hints","suggestion":"def read_config(path: str) -> str:"}],"has_docstring":false,"has_type_hints":false,"summary":"The function reads a file but uses manual open/close which is error-prone. Switch to a context manager and add exception handling."}
"""

class CodeReviewRequest(BaseModel):
    code: str
    context: str = ""

    @field_validator("code")
    @classmethod
    def code_must_be_valid(cls, v):
        if not v.strip():
            raise ValueError("Code cannot be empty")
        if len(v) > 10000:
            raise ValueError("Code exceeds maximum length of 10,000 characters")
        return v

    @field_validator("context")
    @classmethod
    def context_length(cls, v):
        if len(v) > 2000:
            raise ValueError("Context exceeds maximum length of 2,000 characters")
        return v

class ReviewIssue(BaseModel):
    line: int | None
    severity: str
    type: str
    description: str
    suggestion: str

class CodeReviewResponse(BaseModel):
    overall_score: int
    issues: list[ReviewIssue]
    has_docstring: bool
    has_type_hints: bool
    summary: str

@router.post("/code", response_model=CodeReviewResponse)
def review_code(request: CodeReviewRequest):
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")

    check_injection(request.code)
    check_injection(request.context)

    user_message = f"Review this Python function:\n\n{request.code}"
    if request.context:
        user_message += f"\n\nContext: {request.context}"

    try:
        result = call_llm_json(CODE_REVIEW_PROMPT, user_message)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Model returned invalid JSON")

    return result