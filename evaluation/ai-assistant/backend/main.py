import logging

logging.basicConfig(level=logging.INFO)

# Eagerly import presidio_analyzer so the module is fully initialised before
# concurrent requests trigger lazy imports from different threads (which would
# hit a circular-import race in the presidio_analyzer package).
try:
    import presidio_analyzer  # noqa: F401
except ImportError:
    pass  # Optional dependency – endpoints will return clear errors if missing

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import (
    decision,
    evaluation,
    llm,
    presidio_service,
    review,
    upload,
)

app = FastAPI(title="Presidio Evaluation Flow API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(review.router)
app.include_router(evaluation.router)
app.include_router(decision.router)
app.include_router(llm.router)
app.include_router(presidio_service.router)


@app.get("/api/health")
async def health():
    """Return service health status."""
    return {"status": "ok"}
