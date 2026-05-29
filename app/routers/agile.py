from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from app.services.llm import call_llm_json

router = APIRouter(prefix="/agile", tags=["Agile Simulation"])

# --- Shared injection check ---
INJECTION_PATTERNS = [
    "ignore previous instructions", "ignore all instructions",
    "disregard your", "you are now", "new instruction",
    "system prompt", "jailbreak",
]

def check_injection(text: str) -> None:
    lower = text.lower()
    for pattern in INJECTION_PATTERNS:
        if pattern in lower:
            raise HTTPException(status_code=400, detail="Invalid input detected")


# ─────────────────────────────────────────
# 1. STANDUP
# ─────────────────────────────────────────

STANDUP_PROMPT = """
You are an AI scrum master running a daily stand-up.
Given a list of tasks with statuses, respond with ONLY a JSON object. No markdown, no code fences.
{
  "done": ["task descriptions completed since last standup"],
  "in_progress": [
    {"task": "description", "owner": "unknown if not provided", "note": "any blocker or update"}
  ],
  "blocked": [
    {"task": "description", "reason": "why it is blocked", "suggestion": "how to unblock"}
  ],
  "team_health": "green" | "yellow" | "red",
  "summary": "two sentence stand-up summary for the team"
}
team_health: green = no blockers, yellow = some risk, red = blockers threatening the sprint.
"""

class StandupRequest(BaseModel):
    tasks: list[str]

    @field_validator("tasks")
    @classmethod
    def validate_tasks(cls, v):
        if not v:
            raise ValueError("tasks list cannot be empty")
        if len(v) > 50:
            raise ValueError("Maximum 50 tasks per standup")
        return v

@router.post("/standup")
def run_standup(request: StandupRequest):
    for task in request.tasks:
        check_injection(task)
    task_list = "\n".join(f"- {t}" for t in request.tasks)
    user_message = f"Here are today's tasks:\n{task_list}"
    return call_llm_json(STANDUP_PROMPT, user_message)


# ─────────────────────────────────────────
# 2. SPRINT PLANNING
# ─────────────────────────────────────────

SPRINT_PLAN_PROMPT = """
You are an AI scrum master running sprint planning.
Given a product backlog, select and prioritize items for a sprint and estimate effort.
Respond with ONLY a JSON object. No markdown, no code fences.
{
  "sprint_goal": "one sentence goal for this sprint",
  "committed": [
    {
      "item": "backlog item description",
      "priority": "high" | "medium" | "low",
      "effort": "XS" | "S" | "M" | "L" | "XL",
      "rationale": "why this item is in the sprint"
    }
  ],
  "deferred": ["items left in backlog for future sprints"],
  "risk": "none" | "low" | "medium" | "high",
  "summary": "two sentence sprint plan summary"
}
Effort scale: XS=1-2hrs, S=half day, M=1 day, L=2-3 days, XL=full week.
Select a realistic amount of work for a 2-week sprint for a team of 3.
"""

class SprintPlanRequest(BaseModel):
    backlog: list[str]
    team_size: int = 3
    sprint_weeks: int = 2

    @field_validator("backlog")
    @classmethod
    def validate_backlog(cls, v):
        if not v:
            raise ValueError("backlog cannot be empty")
        if len(v) > 100:
            raise ValueError("Maximum 100 backlog items")
        return v

@router.post("/sprint-plan")
def run_sprint_plan(request: SprintPlanRequest):
    for item in request.backlog:
        check_injection(item)
    backlog_list = "\n".join(f"- {i}" for i in request.backlog)
    user_message = (
        f"Team size: {request.team_size} engineers\n"
        f"Sprint length: {request.sprint_weeks} weeks\n\n"
        f"Backlog:\n{backlog_list}"
    )
    return call_llm_json(SPRINT_PLAN_PROMPT, user_message)


# ─────────────────────────────────────────
# 3. RETROSPECTIVE
# ─────────────────────────────────────────

RETRO_PROMPT = """
You are an AI scrum master facilitating a sprint retrospective.
Given a list of sprint outcomes and observations, produce a structured retro.
Respond with ONLY a JSON object. No markdown, no code fences.
{
  "went_well": ["things that went well this sprint"],
  "to_improve": ["things to improve next sprint"],
  "action_items": [
    {"action": "specific thing to do", "owner": "team | dev | pm | unknown", "priority": "high" | "medium" | "low"}
  ],
  "sprint_score": <integer 1-10>,
  "summary": "two sentence retrospective summary"
}
"""

class RetroRequest(BaseModel):
    observations: list[str]

    @field_validator("observations")
    @classmethod
    def validate_observations(cls, v):
        if not v:
            raise ValueError("observations cannot be empty")
        if len(v) > 50:
            raise ValueError("Maximum 50 observations")
        return v

@router.post("/retro")
def run_retro(request: RetroRequest):
    for obs in request.observations:
        check_injection(obs)
    obs_list = "\n".join(f"- {o}" for o in request.observations)
    user_message = f"Sprint observations:\n{obs_list}"
    return call_llm_json(RETRO_PROMPT, user_message)