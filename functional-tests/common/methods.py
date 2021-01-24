import requests
import json
from common.constants import ANONYMIZER_BASE_URL, ANALYZER_BASE_URL

DEFAULT_HEADERS = {"Content-Type": "application/json"}


def anonymize(data):
    response = requests.post(
        f"{ANONYMIZER_BASE_URL}/anonymize", json=data, headers=DEFAULT_HEADERS
    )
    return response.status_code, response.content.decode()


def analyze(data):
    response = requests.post(
        f"{ANALYZER_BASE_URL}/analyze", json=data, headers=DEFAULT_HEADERS
    )
    return response.status_code, json.loads(response.content)
