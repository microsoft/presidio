FROM python:3.8-slim

ARG NAME
ARG SPACY_MODEL
WORKDIR /usr/bin/${NAME}

COPY ./${NAME} /usr/bin/${NAME}

RUN pip install pipenv
RUN pipenv sync
RUN if [ "$SPACY_MODEL" != "" ] ; then pipenv run python -m spacy download "$SPACY_MODEL" ; fi

EXPOSE ${FLASK_RUN_PORT}
CMD pipenv run flask run --host 0.0.0.0