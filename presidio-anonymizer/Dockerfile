# Combined Dockerfile for presidio-anonymizer using Docker's native platform variables
# Usage: docker buildx build --platform linux/amd64,windows/amd64 .

ARG TARGETOS

# Conditional base image selection using native Docker variables
FROM python:3.13-slim AS linux-base
FROM python:3.13-windowsservercore AS windows-base
FROM ${TARGETOS}-base AS base

# Common environment variables
ENV PIP_NO_CACHE_DIR=1
ENV PORT=3000
ENV WORKERS=1

# Set working directory consistently
WORKDIR /app

# Copy dependency files first for better layer caching
COPY ./pyproject.toml /app/

RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry install --no-root --only=main -E server

# Copy application code
COPY . /app/

# Expose port
EXPOSE ${PORT}

# Platform-specific startup command using native Docker variables
RUN if [ "$TARGETOS" = "windows" ]; then \
        echo 'poetry run python app.py' > /app/start.sh; \
    else \
        echo 'poetry run gunicorn -w $WORKERS -b 0.0.0.0:$PORT "app:create_app()"' > /app/start.sh; \
    fi && \
    chmod +x /app/start.sh

CMD ["/bin/sh", "/app/start.sh"]
