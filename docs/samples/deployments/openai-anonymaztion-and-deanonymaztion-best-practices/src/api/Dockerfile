FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN python -m spacy download en_core_web_lg
RUN python -m spacy download es_core_news_sm
RUN python -m spacy download nl_core_news_sm

COPY . .

# Create a non-root user and set ownership
RUN useradd -m -u 1001 presidio && chown -R presidio:presidio /app

USER 1001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
