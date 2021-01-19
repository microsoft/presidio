import requests
import json

ANONYMIZER_BASE_URL = "http://localhost:5001"

ANALYZER_BASE_URL = "http://localhost:3000"

DEFAULT_HEADERS = {"Content-Type": "application/json"}


def anonymize(data):
    response = requests.post(
        f"{ANONYMIZER_BASE_URL}/anonymize", json=data, headers=DEFAULT_HEADERS
    )
    return response.status_code, json.loads(response.content)


def analyze(data):
    return requests.post(
        f"{ANALYZER_BASE_URL}/analyze", json=data, headers=DEFAULT_HEADERS
    )
