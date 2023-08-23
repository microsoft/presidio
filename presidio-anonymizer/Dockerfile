FROM python:3.9-slim

ARG NAME
ENV PIPENV_VENV_IN_PROJECT=1
ENV PIP_NO_CACHE_DIR=1
WORKDIR /usr/bin/${NAME}

COPY ./Pipfile* /usr/bin/${NAME}/
RUN pip install pipenv \
  && pipenv install --deploy

COPY . /usr/bin/${NAME}/

EXPOSE ${PORT}
CMD pipenv run python app.py