from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
from app.services.orchestrator import run_full_analysis

router = APIRouter(prefix="/pipeline", tags=["Full Pipeline"])

class PipelineRequest(BaseModel):
    file_path: str

class PipelineResponse(BaseModel):
    filename: str
    code_review: str
    documentation: str
    bug_triage: str
    sprint_backlog: str
    summary: str

@router.post("/analyze", response_model=PipelineResponse)
def run_pipeline(request: PipelineRequest):
    path = Path(request.file_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
    if not request.file_path.endswith(".py"):
        raise HTTPException(status_code=400, detail="Only Python files supported")

    code = path.read_text(encoding="utf-8")
    return run_full_analysis(code, request.file_path)