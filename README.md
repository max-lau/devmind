# DevMind — AI-Powered Developer Productivity Suite

DevMind is a production-grade multi-agent AI system that automates code review,
documentation generation, bug triage, and sprint planning for software teams.

## What it does

- **Code Review** — AI-powered review with severity ratings, security checks, and fix suggestions
- **Documentation** — Auto-generates Python docstrings and module docs via a 2-agent CrewAI crew
- **Bug Triage** — Classifies and prioritizes bugs with fix time estimates
- **Sprint Planning** — Converts findings into a prioritized sprint backlog with story points
- **Codebase Q&A** — RAG-powered answers about your codebase grounded in real source files
- **GitHub Integration** — Automatically reviews PRs and posts findings as review comments

## Architecture


GitHub PR → Webhook → Job Queue → 4-Agent Pipeline → PR Comment
↓
Code Reviewer → Doc Writer
Bug Triager  → Sprint Planner


## Quick start

### Prerequisites
- Python 3.12+
- OpenAI API key

### Installation

```bash
git clone https://github.com/your-username/devmind.git
cd devmind
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
pip install -e .
```

### Configuration

Create a `.env` file in the root:

OPENAI_API_KEY=your-openai-api-key
GITHUB_TOKEN=your-github-token          # optional, for PR integration
GITHUB_WEBHOOK_SECRET=your-secret       # optional, for webhook verification

### Run the API

```bash
uvicorn main:app --reload
```

API docs available at `http://127.0.0.1:8000/docs`

### CLI commands

```bash
devmind review app/services/llm.py          # AI code review
devmind ask "what endpoints does this API have?"  # RAG codebase Q&A
devmind document app/services/rag.py        # generate documentation
devmind bug "login crashes when email is empty"   # multi-agent bug analysis
devmind pipeline app/services/llm.py        # full 4-agent pipeline
```

### Build the codebase index

```bash
python build_index.py
```

## API endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/review/code` | AI code review |
| POST | `/codebase/ask` | RAG codebase Q&A |
| POST | `/docs/generate` | Generate documentation |
| POST | `/bugs/analyze` | Multi-agent bug analysis |
| POST | `/pipeline/analyze` | Full 4-agent async pipeline |
| GET  | `/pipeline/jobs/{id}` | Poll pipeline job status |
| POST | `/github/webhook` | GitHub PR webhook receiver |
| POST | `/github/analyze-pr` | Manually trigger PR analysis |

## Running tests

```bash
pytest tests/ -v
```

17 tests covering API endpoints and service layer.

## Tech stack

- **FastAPI** — REST API framework
- **LangChain** — LLM orchestration and RAG
- **CrewAI** — Multi-agent crew orchestration
- **ChromaDB** — Vector store for RAG
- **OpenAI GPT-4o-mini** — Language model
- **PyGitHub** — GitHub API client
- **pytest** — Test suite

## Project structure

devmind/
├── app/
│   ├── routers/        # API endpoints
│   └── services/       # Business logic and AI agents
├── tests/              # pytest test suite
├── cli.py              # Installable CLI
├── main.py             # FastAPI app entry point
├── build_index.py      # RAG index builder
└── pyproject.toml      # Package config
