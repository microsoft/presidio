FROM python:3.8-slim

ARG NAME
ENV PIPENV_VENV_IN_PROJECT=1
WORKDIR /usr/bin/${NAME}

RUN apt-get update 
RUN apt-get install tesseract-ocr -y 
RUN tesseract -v

COPY ./Pipfile* /usr/bin/${NAME}/
RUN pip install pipenv
RUN pipenv sync

RUN pipenv run python -m spacy download en_core_web_lg

COPY . /usr/bin/${NAME}/
EXPOSE ${PORT}
CMD pipenv run python app.py