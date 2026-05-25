import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai_tools import FileReadTool
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.2,
    api_key=os.getenv("OPENAI_API_KEY")
)

file_reader = FileReadTool()

# --- Agents ---

code_analyst = Agent(
    role="Senior Code Analyst",
    goal="Read and deeply understand Python source code, identifying all functions, classes, and their purpose",
    backstory="""You are a senior software engineer with 10 years of experience 
    reading and understanding complex Python codebases. You have a talent for 
    quickly grasping what code does and why it exists.""",
    tools=[file_reader],
    llm=llm,
    verbose=True
)

doc_writer = Agent(
    role="Technical Documentation Writer",
    goal="Write clear, accurate, and developer-friendly documentation for Python code",
    backstory="""You are a technical writer who specializes in developer documentation. 
    You write documentation that is concise, accurate, and immediately useful. 
    You always include docstrings, parameter descriptions, return types, and usage examples.""",
    llm=llm,
    verbose=True
)

# --- Tasks ---

def create_analysis_task(file_path: str) -> Task:
    return Task(
        description=f"""Read and analyze the Python file at: {file_path}
        
        Identify:
        1. All functions and their purpose
        2. All classes and their responsibility  
        3. Key dependencies and imports
        4. The overall purpose of this module
        5. Any edge cases or important behaviors""",
        expected_output="A structured analysis of the code including all functions, classes, and module purpose",
        agent=code_analyst
    )

def create_doc_task(file_path: str) -> Task:
    return Task(
        description=f"""Using the code analysis provided, write complete documentation for: {file_path}
        
        Produce:
        1. A module-level docstring explaining the module's purpose
        2. A docstring for every function with: description, Args, Returns, Raises, and Example
        3. A docstring for every class with: description and Attributes
        4. A usage example section at the end showing how to use the key components
        
        Format everything as proper Python docstrings ready to paste into the code.""",
        expected_output="Complete Python documentation with docstrings for all functions and classes",
        agent=doc_writer
    )

# --- Crew runner ---

def document_file(file_path: str) -> str:
    analysis_task = create_analysis_task(file_path)
    doc_task      = create_doc_task(file_path)

    crew = Crew(
        agents=[code_analyst, doc_writer],
        tasks=[analysis_task, doc_task],
        process=Process.sequential,
        verbose=True
    )

    result = crew.kickoff()
    return str(result)