from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.doc_crew import document_file
import os

router = APIRouter(prefix="/docs", tags=["Documentation"])

class DocRequest(BaseModel):
    file_path: str

class DocResponse(BaseModel):
    documentation: str
    file_path: str

@router.post("/generate", response_model=DocResponse)
def generate_docs(request: DocRequest):
    if not request.file_path.strip():
        raise HTTPException(status_code=400, detail="File path cannot be empty")
    if not os.path.exists(request.file_path):
        raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
    if not request.file_path.endswith(".py"):
        raise HTTPException(status_code=400, detail="Only Python files are supported")

    documentation = document_file(request.file_path)
    return {"documentation": documentation, "file_path": request.file_path}