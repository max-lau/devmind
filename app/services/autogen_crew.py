import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.1,
    api_key=os.getenv("OPENAI_API_KEY")
)

PROPOSER_PROMPT = """You are a senior software engineer specializing in debugging.
When given a bug description, propose a detailed root cause analysis and fix.
Format your response with these exact sections:
ROOT CAUSE: (what is causing the bug)
EXPLANATION: (why this causes the problem)
PROPOSED FIX: (exact code or steps to fix it)"""

CRITIC_PROMPT = """You are a principal engineer who reviews bug analyses.
You will receive a bug description and a proposed analysis.
Critically evaluate:
- Is the root cause correct?
- Is the proposed fix complete and safe?
- Are there edge cases the fix misses?
End your response with either:
APPROVED: (summary of final recommendation)
or
NEEDS_REVISION: (what is missing or wrong)"""

def analyze_bug(bug_description: str, code_snippet: str = "") -> str:
    context = f"Bug description: {bug_description}"
    if code_snippet:
        context += f"\n\nRelevant code:\n```python\n{code_snippet}\n```"

    proposal = llm.invoke([
        SystemMessage(content=PROPOSER_PROMPT),
        HumanMessage(content=context)
    ]).content

    critique = llm.invoke([
        SystemMessage(content=CRITIC_PROMPT),
        HumanMessage(content=f"{context}\n\nProposed analysis:\n{proposal}")
    ]).content

    if "NEEDS_REVISION" in critique:
        final = llm.invoke([
            SystemMessage(content=PROPOSER_PROMPT),
            HumanMessage(content=f"{context}\n\nYour previous analysis:\n{proposal}\n\nCritic feedback:\n{critique}\n\nPlease revise your analysis addressing the feedback.")
        ]).content
        return f"## Initial Analysis\n{proposal}\n\n## Critic Review\n{critique}\n\n## Revised Analysis\n{final}"

    return f"## Analysis\n{proposal}\n\n## Review\n{critique}"