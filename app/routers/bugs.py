from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.autogen_crew import analyze_bug

router = APIRouter(prefix="/bugs", tags=["Bug Analysis"])

class BugRequest(BaseModel):
    description: str
    code_snippet: str = ""

class BugResponse(BaseModel):
    analysis: str

@router.post("/analyze", response_model=BugResponse)
def analyze_bug_endpoint(request: BugRequest):
    if not request.description.strip():
        raise HTTPException(status_code=400, detail="Bug description cannot be empty")
    result = analyze_bug(request.description, request.code_snippet)
    return {"analysis": result}