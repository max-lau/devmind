import pytest
from app.services.job_store import create_job, update_job, get_job, list_jobs

def test_create_job():
    job_id = create_job()
    assert job_id is not None
    assert len(job_id) > 0

def test_job_initial_status():
    job_id = create_job()
    job    = get_job(job_id)
    assert job["status"] == "pending"
    assert job["result"] is None
    assert job["error"] is None

def test_update_job_completed():
    job_id = create_job()
    update_job(job_id, "completed", result={"score": 8})
    job = get_job(job_id)
    assert job["status"] == "completed"
    assert job["result"]["score"] == 8

def test_update_job_failed():
    job_id = create_job()
    update_job(job_id, "failed", error="Something went wrong")
    job = get_job(job_id)
    assert job["status"] == "failed"
    assert job["error"] == "Something went wrong"

def test_get_nonexistent_job():
    job = get_job("nonexistent-id")
    assert job is None

def test_list_jobs():
    job_id = create_job()
    jobs   = list_jobs()
    assert isinstance(jobs, list)
    assert any(j["id"] == job_id for j in jobs)

def test_github_comment_formatter():
    from app.services import github_service
    result = {
        "filename":       "test.py",
        "code_review":    "Looks good",
        "bug_triage":     "No bugs",
        "sprint_backlog": "No tasks"
    }
    comment = github_service.format_pipeline_as_comment(result)
    assert "DevMind" in comment
    assert "test.py" in comment
    assert "Looks good" in comment