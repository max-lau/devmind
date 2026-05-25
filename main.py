from fastapi import FastAPI
from app.routers import review, codebase, docs_gen, bugs, pipeline

app = FastAPI(
    title="DevMind API",
    description="AI-powered developer productivity tools",
    version="0.5.0"
)

app.include_router(review.router)
app.include_router(codebase.router)
app.include_router(docs_gen.router)
app.include_router(bugs.router)
app.include_router(pipeline.router)

@app.get("/")
def root():
    return {"status": "DevMind API is running", "version": "0.5.0"}

@app.get("/health")
def health():
    return {"status": "ok", "version": "0.5.0"}