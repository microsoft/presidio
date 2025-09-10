FROM python:3.13-slim

ENV PIP_NO_CACHE_DIR=1

ENV PORT=3000
ENV WORKERS=1

WORKDIR /app

COPY ./pyproject.toml /app/
RUN pip install poetry && poetry install --no-root --only=main -E server

COPY . /app/

EXPOSE ${PORT}
CMD ["./entrypoint.sh"]
