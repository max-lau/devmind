from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from pathlib import Path
from app.services.orchestrator import run_full_analysis
from app.services.job_store import create_job, update_job, get_job, list_jobs

router = APIRouter(prefix="/pipeline", tags=["Full Pipeline"])

class PipelineRequest(BaseModel):
    file_path: str

class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str

def _run_pipeline_job(job_id: str, code: str, filename: str):
    try:
        update_job(job_id, "running")
        result = run_full_analysis(code, filename)
        update_job(job_id, "completed", result=result)
    except Exception as e:
        update_job(job_id, "failed", error=str(e))

@router.post("/analyze", response_model=JobResponse)
def run_pipeline(request: PipelineRequest, background_tasks: BackgroundTasks):
    path = Path(request.file_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
    if not request.file_path.endswith(".py"):
        raise HTTPException(status_code=400, detail="Only Python files supported")

    code = path.read_text(encoding="utf-8")
    job_id = create_job()

    background_tasks.add_task(_run_pipeline_job, job_id, code, request.file_path)

    return {
        "job_id": job_id,
        "status": "pending",
        "message": f"Pipeline started. Poll /pipeline/jobs/{job_id} for results."
    }

@router.get("/jobs/{job_id}")
def get_job_status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.get("/jobs")
def list_all_jobs():
    return list_jobs()