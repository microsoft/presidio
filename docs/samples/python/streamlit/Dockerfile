# Presidio demo — Hugging Face Space (Docker SDK), built with uv.
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# System deps: build tools for native wheels + curl for the healthcheck.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /code

# Resolve & install dependencies (incl. the spaCy models) from the lockfile.
COPY pyproject.toml uv.lock index.md ./
RUN uv sync --frozen --no-dev

# Use the project virtual environment for everything that follows.
ENV VIRTUAL_ENV=/code/.venv \
    PATH=/code/.venv/bin:$PATH

# Run as a non-root user (Hugging Face Spaces convention).
RUN useradd -m -u 1000 user
COPY --chown=user . /code
RUN chown -R user /code
USER user
ENV HOME=/home/user

EXPOSE 7860
HEALTHCHECK CMD curl --fail http://localhost:7860/_stcore/health

CMD ["streamlit", "run", "presidio_streamlit.py", "--server.port=7860", "--server.address=0.0.0.0"]
