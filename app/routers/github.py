import hmac
import hashlib
import os
import json
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel
from app.services.job_store import create_job, update_job
from app.services.orchestrator import run_full_analysis

router = APIRouter(prefix="/github", tags=["GitHub Integration"])

WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "devmind-secret")

def _verify_signature(payload: bytes, signature: str) -> bool:
    expected = "sha256=" + hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)

def _process_pr(job_id: str, repo_name: str, pr_number: int):
    from app.services.github_service import (
        get_pr_changed_files,
        post_pr_comment,
        format_pipeline_as_comment
    )
    try:
        update_job(job_id, "running")
        changed_files = get_pr_changed_files(repo_name, pr_number)

        if not changed_files:
            update_job(job_id, "completed", result={
                "message": "No Python files changed in this PR"
            })
            return

        all_results = []
        combined_comment_parts = []

        for file_info in changed_files[:3]:
            result = run_full_analysis(
                file_info["content"],
                file_info["filename"]
            )
            all_results.append(result)
            combined_comment_parts.append(
                format_pipeline_as_comment(result)
            )

        full_comment = "\n\n---\n\n".join(combined_comment_parts)
        post_pr_comment(repo_name, pr_number, full_comment)

        update_job(job_id, "completed", result={
            "files_analyzed": len(all_results),
            "results": all_results
        })

    except Exception as e:
        update_job(job_id, "failed", error=str(e))

@router.post("/webhook")
async def github_webhook(request: Request, background_tasks: BackgroundTasks):
    payload   = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")

    if not _verify_signature(payload, signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    event = request.headers.get("X-GitHub-Event", "")
    data  = json.loads(payload)

    if event == "pull_request" and data.get("action") in ["opened", "synchronize"]:
        repo_name = data["repository"]["full_name"]
        pr_number = data["pull_request"]["number"]
        job_id    = create_job()
        background_tasks.add_task(_process_pr, job_id, repo_name, pr_number)
        return {
            "message":   "PR analysis started",
            "job_id":    job_id,
            "repo":      repo_name,
            "pr_number": pr_number
        }

    return {"message": f"Event '{event}' received but not processed"}

class ManualPRRequest(BaseModel):
    repo_name: str
    pr_number: int

@router.post("/analyze-pr")
def analyze_pr_manually(request: ManualPRRequest, background_tasks: BackgroundTasks):
    """Manually trigger a PR analysis without a webhook."""
    job_id = create_job()
    background_tasks.add_task(
        _process_pr, job_id, request.repo_name, request.pr_number
    )
    return {
        "job_id":  job_id,
        "status":  "pending",
        "message": f"Analyzing PR #{request.pr_number} in {request.repo_name}"
    }