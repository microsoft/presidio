# Presidio - Data protection and anonymization API

Serviço de anonimização de PII compatível com contexto, conectável e personalizável para texto e imagens.

---

# Build presidio stack
​
## Build images base
```sh
docker build . -f Dockerfile.python.deps -t presidio.azurecr.io/presidio-python-deps:latest \
docker build . -f Dockerfile.golang.deps -t presidio.azurecr.io/presidio-golang-deps:latest \
docker build . -f Dockerfile.golang.base -t presidio.azurecr.io/presidio-golang-base:latest
```
​
## Build services
```sh
docker build . -f presidio-analyzer/Dockerfile -t presidio.azurecr.io/presidio-analyzer:latest \
docker build . -f presidio-anonymizer/Dockerfile -t presidio.azurecr.io/presidio-anonymizer:latest \
docker build . -f presidio-recognizers-store/Dockerfile -t presidio.azurecr.io/presidio-recognizers-store:latest \
docker build . -f presidio-api/Dockerfile -t presidio.azurecr.io/presidio-api:latest \
docker build . -f presidio-datasink/Dockerfile -t presidio.azurecr.io/presidio-datasink:latest \
docker build . -f presidio-ocr/Dockerfile -t presidio.azurecr.io/presidio-ocr:latest \
docker build . -f presidio-collector/Dockerfile -t presidio.azurecr.io/presidio-collector:latest
```
​
## Create network
```sh
docker network create mynetwork
```
​
### Initialize Redis
```sh
docker run --rm --name redis --network mynetwork -d -p 6379:6379 redis
```
​
### Initialize Inalyzer
```sh
docker run --rm --name presidio-analyzer --network mynetwork -p 3000:3000 -e GRPC_PORT=3000 presidio.azurecr.io/presidio-analyzer:latest
```
​
### Initialize Anonymizer
```sh
docker run --rm --name presidio-anonymizer --network mynetwork -p 3001:3001 -e GRPC_PORT=3001 presidio.azurecr.io/presidio-anonymizer:latest
```
​
### Initialize Recognizer
```sh
docker run --rm --name presidio-recognizers-store --network mynetwork -p 3004:3004 -e GRPC_PORT=3004 -e REDIS_URL=redis:6379 presidio.azurecr.io/presidio-recognizers-store:latest
```
​
### Initialize Apis
```sh
docker run --rm --name presidio-api --network mynetwork -p 8080:8080 -e WEB_PORT=8080 -e ANALYZER_SVC_ADDRESS=presidio-analyzer:3000 -e ANONYMIZER_SVC_ADDRESS=presidio-anonymizer:3001 -e RECOGNIZERS_STORE_SVC_ADDRESS=presidio-recognizers-store:3004 presidio.azurecr.io/presidio-api:latest
```
​
## Optional services
​
### Initialize Datasink
```sh
docker run --rm --name presidio-datasink --network mynetwork -p 5000:5000 presidio.azurecr.io/presidio-datasink:latest
```
​
### Initialize Scheduler
```sh
docker run --rm --name presidio-scheduler --network -e DATASINK_GRPC_PORT=5000 -e REDIS_URL=redis:6379 -e ANALYZER_SVC_ADDRESS=presidio-analyzer:3000 -e ANONYMIZER_SVC_ADDRESS=presidio-anonymizer:3001 presidio.azurecr.io/presidio-scheduler:latest
```
​
### Initialize OCR
```sh
docker run --rm --name presidio-ocr --network mynetwork -p 3003:3003 presidio.azurecr.io/presidio-ocr:latest
```
​
### Initialize Collector ???
```sh
docker run --rm --name presidio-collector --network mynetwork -e REDIS_URL=redis:6379 -e ANALYZER_SVC_ADDRESS=presidio-analyzer:3000 -e ANONYMIZER_SVC_ADDRESS=presidio-anonymizer:3001 presidio.azurecr.io/presidio-collector:latest
```
​
​
## Examples Apis
​
### Recognizers
​
#### Create Recognizers
```sh
curl --location --request POST '127.0.0.1:8080/api/v1/analyzer/recognizers/1' \
--header 'Content-Type: application/json' \
--data-raw '{
    "value": {
        "blacklist": [
            "velit sint aliquip",
            "elit consequat"
        ],
        "contextPhrases": [
            "eu ullamco aute",
            "esse velit qui"
        ],
        "entity": "commodo mollit qui",
        "language": "consectetur cupidatat ad ullamco officia",
        "name": "deserunt in aliqua ullamco",
        "patterns": [
            {
                "name": "sed quis proident",
                "regex": "aute proident et irure",
                "score": -74888500.18834418
            },
            {
                "name": "voluptate tempor",
                "regex": "sed ",
                "score": -66246829.50692073
            }
        ]
    }
}'
```
​
#### List Recognizers By ID
```sh
curl --location --request GET '127.0.0.1:8080/api/v1/analyzer/recognizers/1'
```
​
#### List all Recognizers
```sh
curl --location --request GET '127.0.0.1:8080/api/v1/analyzer/recognizers/'
```
​
​
### Analyzers
​
#### Analyze text
>request
```sh
curl --location --request POST '127.0.0.1:8080/api/v1/projects/event-tracking/analyze' \
--header 'Content-Type: application/json' \
--data-raw '{
   "text":"John Smith lives in New York. We met yesterday morning in Seattle. I called him before on (212) 555-1234 to verify the appointment. He also told me that his drivers license is AC333991",
   "analyzeTemplate":{
      "allFields":true
   }
}'
```
>response
```json
[
    {
        "field": {
            "name": "PERSON"
        },
        "score": 0.85,
        "location": {
            "end": 10,
            "length": 10
        }
    },
    {
        "field": {
            "name": "LOCATION"
        },
        "score": 0.85,
        "location": {
            "start": 20,
            "end": 28,
            "length": 8
        }
    },
    {
        "field": {
            "name": "DATE_TIME"
        },
        "score": 0.85,
        "location": {
            "start": 37,
            "end": 46,
            "length": 9
        }
    },
    {
        "field": {
            "name": "DATE_TIME"
        },
        "score": 0.85,
        "location": {
            "start": 47,
            "end": 54,
            "length": 7
        }
    },
    {
        "field": {
            "name": "LOCATION"
        },
        "score": 0.85,
        "location": {
            "start": 58,
            "end": 65,
            "length": 7
        }
    },
    {
        "field": {
            "name": "PHONE_NUMBER"
        },
        "score": 0.7,
        "location": {
            "start": 90,
            "end": 104,
            "length": 14
        }
    },
    {
        "field": {
            "name": "US_DRIVER_LICENSE"
        },
        "score": 0.65,
        "location": {
            "start": 176,
            "end": 184,
            "length": 8
        }
    }
]
``


[Presidio repositório](https://github.com/microsoft/presidio).

