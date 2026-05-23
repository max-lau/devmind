import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

SYSTEM_PROMPT = """
You are a bug triage assistant for a software engineering team.

When given a GitHub issue title, you must respond with ONLY a JSON object.
No explanation, no markdown, no code fences. Raw JSON only.

The JSON must have exactly these fields:
{
  "severity": "critical" | "high" | "medium" | "low",
  "category": "bug" | "performance" | "security" | "feature" | "docs",
  "summary": "one sentence description of the issue",
  "suggested_owner": "frontend" | "backend" | "devops" | "unknown",
  "needs_immediate_attention": true | false
}
"""

def analyze_issue(issue_title: str) -> dict:
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Issue title: {issue_title}"}
            ],
            "temperature": 0.1
        }
    )
    raw = response.json()["choices"][0]["message"]["content"]
    return json.loads(raw)

if __name__ == "__main__":
    test_issues = [
        "app crashes when uploading files larger than 10mb",
        "login page loads slowly on mobile",
        "user passwords stored in plain text",
        "add dark mode to dashboard",
    ]

    for issue in test_issues:
        print(f"\nIssue: {issue}")
        result = analyze_issue(issue)
        print(json.dumps(result, indent=2))