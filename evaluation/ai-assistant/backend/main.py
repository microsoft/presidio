from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import analysis, datasets, decision, evaluation, review, sampling, upload

app = FastAPI(title="Presidio Evaluation Flow API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(datasets.router)
app.include_router(upload.router)
app.include_router(sampling.router)
app.include_router(analysis.router)
app.include_router(review.router)
app.include_router(evaluation.router)
app.include_router(decision.router)


@app.get("/api/health")
async def health():
    """Return service health status."""
    return {"status": "ok"}
