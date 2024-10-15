# API Readme

## Install requirements

```bash
cd src/api
pip install -r requirements.txt
```

### Set environment variables

Add `.env` file in the `/src/api` folder:

```bash
cp .env.sample .env
```

Then edit this configuration according to your setup.

## Run locally

```bash
uvicorn main:app --host 0.0.0.0 --port 8080
```

## Run as a docker container

```bash
docker build -t api .
docker run -d -p 8080:80 --env-file .env api
```
