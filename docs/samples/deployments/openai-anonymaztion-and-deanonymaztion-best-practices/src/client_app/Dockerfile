FROM python:3.10-slim@sha256:e508a34e5491225a76fbb9e0f43ebde1f691c6a689d096d7510cf7fb17d4ba6f

WORKDIR /app

COPY requirements-locked.txt .

RUN pip install --no-cache-dir --require-hashes -r requirements-locked.txt

COPY . .

# Create a non-root user and set ownership
RUN useradd -m -u 1001 presidio && chown -R presidio:presidio /app

USER 1001

CMD ["python", "serve.py"]
