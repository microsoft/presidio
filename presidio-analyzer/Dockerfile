FROM python:3.8-slim

ARG NAME
ARG SPACY_MODEL=en_core_web_lg
ENV PIPENV_VENV_IN_PROJECT=1
WORKDIR /usr/bin/${NAME}

COPY ./Pipfile* /usr/bin/${NAME}/
RUN pip install pipenv
RUN pipenv sync
RUN pipenv run python -m spacy download ${SPACY_MODEL}

COPY . /usr/bin/${NAME}/
EXPOSE ${FLASK_RUN_PORT}
CMD pipenv run python app.py --host 0.0.0.0