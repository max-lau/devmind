import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.llm import call_llm_json

router = APIRouter(prefix="/review", tags=["Code Review"])

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

Examples:

Function:
def divide(a, b):
    return a / b

{"overall_score":4,"issues":[{"line":2,"severity":"critical","type":"bug","description":"No check for division by zero","suggestion":"Add 'if b == 0: raise ValueError(\"Cannot divide by zero\")' before the return"},{"line":1,"severity":"low","type":"style","description":"Missing type hints","suggestion":"Change signature to: def divide(a: float, b: float) -> float:"}],"has_docstring":false,"has_type_hints":false,"summary":"The function works for the happy path but will crash with a ZeroDivisionError when b is 0. Needs input validation and type hints."}
"""

class CodeReviewRequest(BaseModel):
    code: str
    context: str = ""

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

    user_message = f"Review this Python function:\n\n{request.code}"
    if request.context:
        user_message += f"\n\nContext: {request.context}"

    try:
        result = call_llm_json(CODE_REVIEW_PROMPT, user_message)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Model returned invalid JSON")

    return result