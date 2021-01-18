FROM python:3.7

ARG NAME
ARG PORT
WORKDIR /usr/bin/${NAME}

RUN pip install pipenv

COPY ./${NAME} /usr/bin/${NAME}

RUN pipenv lock --requirements > requirements.txt
RUN pip install -r requirements.txt

EXPOSE ${PORT}
CMD flask run