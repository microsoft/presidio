FROM python:3.13-slim

ENV PIP_NO_CACHE_DIR=1

ENV PORT=3000
ENV WORKERS=1

WORKDIR /app

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY ./pyproject.toml ./poetry.lock /app/
RUN pip install poetry && poetry install --no-root --only=main -E server

COPY . /app/

EXPOSE ${PORT}
HEALTHCHECK --interval=30s --timeout=3s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1
CMD ["./entrypoint.sh"]
