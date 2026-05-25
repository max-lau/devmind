import os
from crewai import Crew, Process
from app.services.agents import (
    get_code_reviewer,
    get_doc_writer,
    get_bug_triager,
    get_sprint_planner
)
from app.services.tasks import (
    code_review_task,
    documentation_task,
    bug_triage_task,
    sprint_planning_task
)

def run_full_analysis(code: str, filename: str) -> dict:
    """Run the full 4-agent DevMind analysis pipeline."""

    # Instantiate agents
    reviewer  = get_code_reviewer()
    writer    = get_doc_writer()
    triager   = get_bug_triager()
    planner   = get_sprint_planner()

    # Create tasks — each builds on the previous
    t1 = code_review_task(reviewer, code, filename)
    t2 = documentation_task(writer, code, filename)
    t3 = bug_triage_task(triager, "See code review findings from previous task.", filename)
    t4 = sprint_planning_task(planner, "See bug triage findings from previous task.", filename)

    # Assemble and run the crew
    crew = Crew(
        agents=[reviewer, writer, triager, planner],
        tasks=[t1, t2, t3, t4],
        process=Process.sequential,
        verbose=True
    )

    result = crew.kickoff()

    return {
        "filename": filename,
        "code_review":     str(t1.output) if t1.output else "",
        "documentation":   str(t2.output) if t2.output else "",
        "bug_triage":      str(t3.output) if t3.output else "",
        "sprint_backlog":  str(t4.output) if t4.output else "",
        "summary":         str(result)
    }