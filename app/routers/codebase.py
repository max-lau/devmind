from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.rag import query_codebase

router = APIRouter(prefix="/codebase", tags=["Codebase Q&A"])

class CodebaseQuestion(BaseModel):
    question: str

class CodebaseAnswer(BaseModel):
    answer: str
    sources: list[str]

@router.post("/ask", response_model=CodebaseAnswer)
def ask_codebase(request: CodebaseQuestion):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    return query_codebase(request.question)