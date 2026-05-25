import uuid
from datetime import datetime
from typing import Any

# In-memory job store — replaced by Redis in Phase 4
_jobs: dict[str, dict] = {}

def create_job() -> str:
    job_id = str(uuid.uuid4())
    _jobs[job_id] = {
        "id": job_id,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        "result": None,
        "error": None
    }
    return job_id

def update_job(job_id: str, status: str, result: Any = None, error: str = None):
    if job_id in _jobs:
        _jobs[job_id]["status"] = status
        _jobs[job_id]["result"] = result
        _jobs[job_id]["error"] = error
        _jobs[job_id]["updated_at"] = datetime.utcnow().isoformat()

def get_job(job_id: str) -> dict | None:
    return _jobs.get(job_id)

def list_jobs() -> list[dict]:
    return list(_jobs.values())