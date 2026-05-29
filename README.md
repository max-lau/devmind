# DevMind — AI-Powered Developer Productivity Suite

DevMind is a production-grade multi-agent AI system that automates code review,
documentation generation, bug triage, sprint planning, and agile simulation for software teams.

Live API: https://devmind-production-c756.up.railway.app

---

## What it does

| Agent | Endpoint | Description |
|-------|----------|-------------|
| Code Reviewer | `POST /review/code` | Reviews Python functions with severity ratings, security checks, and fix suggestions |
| Codebase Q&A | `POST /codebase/ask` | RAG-powered answers grounded in real source files |
| Doc Writer | `POST /docs/generate` | Auto-generates docstrings and module docs via a 2-agent CrewAI crew |
| Bug Triager | `POST /bugs/analyze` | Classifies and prioritizes bugs with fix time estimates |
| Pipeline | `POST /pipeline/analyze` | Full 4-agent async pipeline: review → docs → bugs → sprint |
| GitHub | `POST /github/analyze-pr` | Reviews PRs and posts findings as GitHub review comments |
| Scrum Master | `POST /agile/standup` | Runs a daily stand-up from a task list |
| Scrum Master | `POST /agile/sprint-plan` | Converts a backlog into a prioritized sprint with effort estimates |
| Scrum Master | `POST /agile/retro` | Produces a structured sprint retrospective with action items |

---

## Architecture

Client
│
▼
FastAPI (main.py)
│  X-API-Key auth on all routes
│  Request logging middleware (Loguru)
│  Error tracking (Sentry)
│
├── /review      → LangChain + GPT-4o-mini
├── /codebase    → ChromaDB RAG + GPT-4o-mini
├── /docs        → CrewAI 2-agent crew
├── /bugs        → LangChain + GPT-4o-mini
├── /pipeline    → Async job queue → 4-agent orchestrator
├── /github      → PyGitHub webhook + PR review
└── /agile       → LangChain + GPT-4o-mini (standup, sprint-plan, retro)

GitHub PR → Webhook → Job Queue → 4-Agent Pipeline → PR Comment

---

## Quick start

### Prerequisites
- Python 3.12+
- OpenAI API key

### Installation

```bash
git clone https://github.com/max-lau/devmind.git
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
DEVMIND_API_KEY=your-api-key          # default: dev-local-key
GITHUB_TOKEN=your-github-token        # optional, for PR integration
GITHUB_WEBHOOK_SECRET=your-secret     # optional, for webhook verification
SENTRY_DSN=your-sentry-dsn           # optional, for error tracking

### Run locally

```bash
uvicorn main:app --reload
```

API docs: http://127.0.0.1:8000/docs

### Run with Docker

```bash
docker build -t devmind .
docker run -p 8000:8000 --env-file .env devmind
```

---

## API reference

All endpoints require the header: `X-API-Key: your-api-key`

### Code Review

POST /review/code
{"code": "def divide(a, b):\n    return a / b"}

### Codebase Q&A

POST /codebase/ask
{"question": "what endpoints does this API have?"}

### Documentation

POST /docs/generate
{"file_path": "app/services/llm.py"}

### Bug Analysis

POST /bugs/analyze
{"title": "Login crashes when email is empty", "description": "..."}

### Full Pipeline (async)


POST /pipeline/analyze
{"file_path": "app/services/llm.py"}
GET /pipeline/jobs/{job_id}   ← poll for result

### GitHub PR Review

POST /github/analyze-pr
{"repo": "owner/repo", "pr_number": 42}


### Agile — Stand-up

POST /agile/standup
{"tasks": ["DONE: fixed login bug", "IN PROGRESS: dashboard", "BLOCKED: API keys"]}


### Agile — Sprint Planning

POST /agile/sprint-plan
{"backlog": ["Add auth", "Build dashboard", "Fix payment bug", "Write docs"]}

### Agile — Retrospective

POST /agile/retro
{"observations": ["Shipped on time", "Standups too long", "No staging env"]}

---

## CLI

```bash
devmind review app/services/llm.py
devmind ask "what endpoints does this API have?"
devmind document app/services/rag.py
devmind bug "login crashes when email is empty"
devmind pipeline app/services/llm.py
```

---

## Eval harness

```bash
uvicorn main:app --reload   # terminal 1
python evals/run_evals.py   # terminal 2
```

Runs 5 test cases against the code review agent and enforces a quality gate of ≥80%.
Baseline score: 100% (44/44 points) at temperature=0.

---

## Security

| Control | Detail |
|---------|--------|
| API key auth | `X-API-Key` header required on all endpoints |
| Input validation | Code ≤10,000 chars, context ≤2,000 chars via Pydantic |
| Prompt injection defense | 7-pattern blocklist on all user inputs |
| Non-root container | `devmind` user in Dockerfile |
| Scoped OpenAI key | Model capabilities only, $10/month spend cap |
| Secrets at runtime | Injected via Railway variables, never in image |
| HTTPS | Automatic TLS via Railway |

---

## Tech stack

- **FastAPI** — REST API framework
- **LangChain** — LLM orchestration and RAG
- **CrewAI** — Multi-agent crew orchestration
- **ChromaDB** — Vector store for RAG
- **OpenAI GPT-4o-mini** — Language model (temperature=0 for determinism)
- **PyGitHub** — GitHub API client
- **Loguru** — Structured logging
- **Sentry** — Error tracking
- **Docker + GHCR** — Containerization and image registry
- **Railway** — Cloud deployment
- **GitHub Actions** — CI/CD pipeline
- **pytest** — Test suite

---

## Project structure

devmind/
├── app/
│   ├── routers/        # API endpoints (review, codebase, docs, bugs, pipeline, github, agile)
│   ├── services/       # Business logic and AI agents
│   └── logger.py       # Structured logging + Sentry setup
├── evals/
│   ├── eval_cases.json # Test cases for code review agent
│   └── run_evals.py    # Eval harness with quality gate
├── tests/              # pytest test suite (17 tests)
├── .github/workflows/  # CI/CD — build, test, publish to GHCR
├── cli.py              # Installable CLI
├── main.py             # FastAPI app entry point
├── build_index.py      # RAG index builder
├── Dockerfile          # Non-root production container
└── pyproject.toml      # Package config


---

## Deployment

DevMind runs on Railway, deployed automatically on every push to `main` via GitHub Actions.
The Docker image is published to GitHub Container Registry (ghcr.io).

Push to main
→ GitHub Actions: test → build → push image to GHCR
→ Railway: pull image → deploy → live in ~2 minutes


