FROM python:3.9-slim

ARG NAME
ENV PIP_NO_CACHE_DIR=1
WORKDIR /usr/bin/${NAME}

COPY ./pyproject.toml /usr/bin/${NAME}/
COPY ./README.md /usr/bin/${NAME}/
COPY ./VERSION /usr/bin/${NAME}/
RUN pip install pdm && pdm install --prod -G server --no-lock --no-editable

COPY . /usr/bin/${NAME}/

EXPOSE ${PORT}
CMD pdm run python app.py