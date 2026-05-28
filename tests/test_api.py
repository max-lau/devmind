import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
AUTH = {"X-API-Key": "dev-local-key"}

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "DevMind API is running"

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_review_code_empty_input():
    response = client.post("/review/code", json={"code": "", "context": ""}, headers=AUTH)
    assert response.status_code in (400, 422)
def test_review_code_valid_input():
    response = client.post(
        "/review/code",
        json={"code": "def add(a, b):\n    return a + b", "context": "simple function"},
        headers=AUTH
    )
    assert response.status_code == 200
    data = response.json()
    assert "overall_score" in data
    assert "issues" in data
    assert "summary" in data
    assert isinstance(data["overall_score"], int)
    assert 1 <= data["overall_score"] <= 10

def test_codebase_ask_empty_question():
    response = client.post("/codebase/ask", json={"question": ""}, headers=AUTH)
    assert response.status_code == 400

def test_pipeline_file_not_found():
    response = client.post(
        "/pipeline/analyze",
        json={"file_path": "nonexistent_file.py"},
        headers=AUTH
    )
    assert response.status_code == 404

def test_pipeline_non_python_file():
    response = client.post(
        "/pipeline/analyze",
        json={"file_path": "README.md"},
        headers=AUTH
    )
    assert response.status_code == 400

def test_pipeline_returns_job_id():
    response = client.post(
        "/pipeline/analyze",
        json={"file_path": "app/services/llm.py"},
        headers=AUTH
    )
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "pending"

def test_job_polling():
    submit = client.post(
        "/pipeline/analyze",
        json={"file_path": "app/services/llm.py"},
        headers=AUTH
    )
    job_id = submit.json()["job_id"]
    poll = client.get(f"/pipeline/jobs/{job_id}", headers=AUTH)
    assert poll.status_code == 200
    assert poll.json()["id"] == job_id
    assert poll.json()["status"] in ["pending", "running", "completed", "failed"]

def test_job_not_found():
    response = client.get("/pipeline/jobs/fake-job-id-123", headers=AUTH)
    assert response.status_code == 404