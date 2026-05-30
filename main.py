import os
from fastapi import FastAPI, Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from app.routers import review, codebase, docs_gen, bugs, pipeline, github, agile
from app.logger import logger, setup_sentry

setup_sentry()

API_KEY = os.getenv("DEVMIND_API_KEY", "dev-local-key")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def require_api_key(key: str = Security(api_key_header)):
    if key != API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing API key")
    return key

app = FastAPI(title="DevMind API", description="AI-powered developer productivity tools", version="1.0.0")

app.include_router(review.router, dependencies=[Security(require_api_key)])
app.include_router(codebase.router, dependencies=[Security(require_api_key)])
app.include_router(docs_gen.router, dependencies=[Security(require_api_key)])
app.include_router(bugs.router, dependencies=[Security(require_api_key)])
app.include_router(pipeline.router, dependencies=[Security(require_api_key)])
app.include_router(github.router, dependencies=[Security(require_api_key)])
app.include_router(agile.router, dependencies=[Security(require_api_key)])

@app.middleware("http")
async def log_requests(request, call_next):
    import time
    start = time.time()
    response = await call_next(request)
    duration = round((time.time() - start) * 1000)
    logger.info(f"{request.method} {request.url.path} -> {response.status_code} ({duration}ms)")
    return response

@app.get("/")
def root():
    return {"status": "DevMind API is running", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0"}
