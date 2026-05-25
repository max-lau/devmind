from crewai import Task
from crewai import Agent

def code_review_task(agent: Agent, code: str, filename: str) -> Task:
    return Task(
        description=f"""Review the following Python code from file '{filename}'.

Analyze it thoroughly for:
1. Bugs and logic errors
2. Security vulnerabilities (SQL injection, XSS, unsafe deserialization, etc.)
3. Performance issues (N+1 queries, unnecessary loops, memory leaks)
4. Code style and maintainability issues
5. Missing error handling
6. Missing type hints or docstrings

Code to review:
```python
{code}
```

Be specific — reference exact line numbers where possible.""",
        expected_output="""A structured code review containing:
- Overall quality score (1-10)
- List of issues found (each with: severity, type, line number, description, suggested fix)
- Summary assessment
- Whether the code is safe to merge""",
        agent=agent
    )

def documentation_task(agent: Agent, code: str, filename: str, review_findings: str = "") -> Task:
    return Task(
        description=f"""Write complete Python documentation for the file '{filename}'.

Code:
```python
{code}
```

Previous review findings to incorporate:
{review_findings if review_findings else "No prior review available."}

Generate:
1. Module-level docstring
2. Docstrings for every function and class
3. Each docstring must include: description, Args, Returns, Raises, Example
4. A usage example at the module level""",
        expected_output="""Complete Python documentation ready to paste into the file,
including module docstring, all function/class docstrings with Args/Returns/Raises/Example sections,
and a usage example.""",
        agent=agent
    )

def bug_triage_task(agent: Agent, review_findings: str, filename: str) -> Task:
    return Task(
        description=f"""Based on the following code review findings for '{filename}', 
perform bug triage:

{review_findings}

For each bug or issue found:
1. Assign severity: CRITICAL / HIGH / MEDIUM / LOW
2. Assign category: security / bug / performance / style / maintainability
3. Estimate fix time: <1h / 1-4h / 1-2d / 3-5d
4. Assign to team: backend / frontend / devops / any
5. Write a concrete, actionable fix description
6. Flag any issues that block deployment""",
        expected_output="""A triage report with each issue classified by severity, category,
fix time estimate, team assignment, and concrete fix instructions.
Include a deployment blocker flag for critical issues.""",
        agent=agent
    )

def sprint_planning_task(agent: Agent, triage_report: str, filename: str) -> Task:
    return Task(
        description=f"""Convert the following bug triage report for '{filename}' 
into a prioritized sprint backlog:

{triage_report}

Create sprint tasks that:
1. Are specific and actionable (a developer can start immediately)
2. Have story point estimates (1, 2, 3, 5, 8, 13)
3. Are ordered by priority (deployment blockers first)
4. Include acceptance criteria for each task
5. Group related tasks together
6. Identify quick wins (high value, low effort)

Assume a team velocity of 20 story points per sprint.""",
        expected_output="""A prioritized sprint backlog with tasks ordered by priority,
each containing: title, description, story points, acceptance criteria, and priority level.
Include a sprint summary showing total points and recommended sprint allocation.""",
        agent=agent
    )