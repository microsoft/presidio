FROM python:3.8-slim

ARG NAME
ARG NLP_CONF_FILE=conf/default.yaml
ENV PIPENV_VENV_IN_PROJECT=1
WORKDIR /usr/bin/${NAME}

COPY ./Pipfile* /usr/bin/${NAME}/
RUN pip install pipenv
RUN pipenv sync

COPY . /usr/bin/${NAME}/

# install nlp models specified in conf/default.yaml
RUN pipenv run python install_nlp_models.py --conf_file ${NLP_CONF_FILE}

EXPOSE ${PORT}
CMD pipenv run python app.py --host 0.0.0.0