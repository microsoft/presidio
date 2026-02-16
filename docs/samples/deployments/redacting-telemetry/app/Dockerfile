FROM python:3.11-slim@sha256:0b23cfb7425d065008b778022a17b1551c82f8b4866ee5a7a200084b7e2eafbf

WORKDIR /app

COPY requirements-locked.txt .
RUN pip install --no-cache-dir --require-hashes -r requirements-locked.txt

COPY main.py presidio_client.py ./

CMD ["python", "main.py"]
