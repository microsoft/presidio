# Running the App

## Backend

**Important:** Run `poetry run` from the `backend/` directory (not the repo root) so Poetry uses the correct virtualenv with `presidio-analyzer` installed.

```bash
cd evaluation/ai-assistant/backend
poetry install            # first time only — installs presidio-analyzer + deps
poetry run python -m spacy download en_core_web_sm  # required by presidio-evaluator
poetry run uvicorn main:app --reload --reload-dir . --port 8000 --log-level info
```

> `--reload-dir .` scopes file watching to the backend directory only, preventing restarts when spaCy downloads models into site-packages.

## Frontend

```bash
cd evaluation/ai-assistant
npm install
npm run dev
```

Opens at http://localhost:5173 (proxies `/api` to backend).
