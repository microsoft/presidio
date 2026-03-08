# Running the App

## Backend

```bash
cd evaluation/ai-assistant/backend
poetry install
poetry run uvicorn main:app --reload --port 8000
```

## Frontend

```bash
cd evaluation/ai-assistant
npm install
npm run dev
```

Opens at http://localhost:5173 (proxies `/api` to backend).
