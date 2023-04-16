FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip3 install -r requirements.txt
RUN pip3 install https://huggingface.co/spacy/en_core_web_sm/resolve/main/en_core_web_sm-any-py3-none-any.whl
RUN pip3 install https://huggingface.co/spacy/en_core_web_lg/resolve/main/en_core_web_lg-any-py3-none-any.whl

EXPOSE 7860

COPY . /code

RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
	PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

COPY --chown=user . $HOME/app

HEALTHCHECK CMD curl --fail http://localhost:7860/_stcore/health

CMD python -m streamlit run presidio_streamlit.py --server.port=7860 --server.address=0.0.0.0