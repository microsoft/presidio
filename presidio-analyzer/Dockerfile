FROM python:3.9-slim

ARG NAME
ARG NLP_CONF_FILE=conf/default.yaml
ENV PIPENV_VENV_IN_PROJECT=1
ENV PIP_NO_CACHE_DIR=1
WORKDIR /usr/bin/${NAME}

COPY ./Pipfile* /usr/bin/${NAME}/
RUN pip install pipenv \
  && pipenv sync
# install nlp models specified in conf/default.yaml
COPY ./install_nlp_models.py /usr/bin/${NAME}/
COPY ${NLP_CONF_FILE} /usr/bin/${NAME}/${NLP_CONF_FILE}
RUN pipenv run python install_nlp_models.py --conf_file ${NLP_CONF_FILE}

COPY . /usr/bin/${NAME}/
EXPOSE ${PORT}
CMD pipenv run python app.py --host 0.0.0.0