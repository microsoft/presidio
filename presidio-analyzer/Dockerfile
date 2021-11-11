FROM python:3.9-slim

ARG NAME
ARG NLP_CONF_FILE=conf/default.yaml
ENV PIPENV_VENV_IN_PROJECT=1
WORKDIR /usr/bin/${NAME}

COPY ./Pipfile* /usr/bin/${NAME}/
RUN pip install pipenv
RUN pipenv install
# install nlp models specified in conf/default.yaml
COPY ./install_nlp_models.py /usr/bin/${NAME}/
COPY ${NLP_CONF_FILE} /usr/bin/${NAME}/${NLP_CONF_FILE}
RUN pipenv run pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.2.0/en_core_web_lg-3.2.0-py3-none-any.whl

COPY . /usr/bin/${NAME}/
EXPOSE ${PORT}
CMD pipenv run python app.py --host 0.0.0.0