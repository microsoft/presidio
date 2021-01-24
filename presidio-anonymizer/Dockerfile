FROM python:3.8-slim

ARG NAME
ENV PIPENV_VENV_IN_PROJECT=1
WORKDIR /usr/bin/${NAME}

COPY ./Pipfile* /usr/bin/${NAME}/
RUN pip install pipenv
RUN pipenv sync

COPY . /usr/bin/${NAME}/

# TODO: [ADO-2680] Use FLASK_RUN_PORT and flask run --host 0.0.0.0
EXPOSE ${PORT}
CMD pipenv run python app.py