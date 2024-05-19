FROM python:3.9-slim

ARG NAME
ENV PIPENV_VENV_IN_PROJECT=1
ENV PIP_NO_CACHE_DIR=1
WORKDIR /usr/bin/${NAME}

COPY ./pyproject.toml /usr/bin/${NAME}/
COPY ./README.md /usr/bin/${NAME}/
COPY ./VERSION /usr/bin/${NAME}/
RUN pip install pdm && pdm install --prod --no-lock --no-editable

COPY . /usr/bin/${NAME}/

EXPOSE ${PORT}
CMD pipenv run python app.py