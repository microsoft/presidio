FROM python:3.8-slim

ARG NAME
ENV PIPENV_VENV_IN_PROJECT=1
ENV PIP_NO_CACHE_DIR=1
WORKDIR /usr/bin/${NAME}

RUN apt-get update \
  && apt-get install tesseract-ocr -y \
  && rm -rf /var/lib/apt/lists/* \
  && tesseract -v

RUN apt-get update \ 
  && apt-get install ffmpeg libsm6 libxext6  -y


COPY ./Pipfile* /usr/bin/${NAME}/
RUN pip install pipenv \
  && pipenv install --deploy \
  && pipenv run python -m spacy download en_core_web_lg

COPY . /usr/bin/${NAME}/
EXPOSE ${PORT}
CMD pipenv run python app.py