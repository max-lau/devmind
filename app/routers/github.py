import hmac
import hashlib
import os
import json
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
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

def _process_pr(job_id: str, pr_data: dict):
    try:
        update_job(job_id, "running")
        pr_title  = pr_data.get("pull_request", {}).get("title", "Unknown PR")
        pr_body   = pr_data.get("pull_request", {}).get("body", "")
        repo_name = pr_data.get("repository", {}).get("full_name", "unknown/repo")

        # Simulate analyzing the PR description as code context
        # In Week 11 we'll add actual GitHub API calls to fetch changed files
        pseudo_code = f"""
# Pull Request: {pr_title}
# Repository: {repo_name}
# Description: {pr_body}

# This PR is being analyzed by DevMind.
# Full file analysis requires GitHub API integration (Week 11).
"""
        result = run_full_analysis(pseudo_code, f"PR: {pr_title}")
        update_job(job_id, "completed", result=result)
    except Exception as e:
        update_job(job_id, "failed", error=str(e))

@router.post("/webhook")
async def github_webhook(request: Request, background_tasks: BackgroundTasks):
    payload = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")

    if not _verify_signature(payload, signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    event = request.headers.get("X-GitHub-Event", "")
    data  = json.loads(payload)

    if event == "pull_request" and data.get("action") in ["opened", "synchronize"]:
        job_id = create_job()
        background_tasks.add_task(_process_pr, job_id, data)
        return {
            "message": "PR analysis started",
            "job_id": job_id,
            "event": event,
            "action": data.get("action")
        }

    return {"message": f"Event '{event}' received but not processed"}