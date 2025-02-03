FROM python:3.9-slim

ARG NAME
ENV PIP_NO_CACHE_DIR=1

ENV PORT=3000
ENV WORKERS=1

WORKDIR /usr/bin/${NAME}

COPY ./pyproject.toml /usr/bin/${NAME}/
COPY ./README.md /usr/bin/${NAME}/
RUN pip install poetry && poetry install --no-root --only=main -E server

COPY . /usr/bin/${NAME}/

EXPOSE ${PORT}
CMD poetry run gunicorn -w $WORKERS -b 0.0.0.0:$PORT 'app:create_app()'