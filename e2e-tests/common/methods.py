import os
import requests
from common.constants import ANONYMIZER_BASE_URL, ANALYZER_BASE_URL

DEFAULT_HEADERS = {"Content-Type": "application/json"}
ANALYZER_BASE_URL = os.environ.get("ANALYZER_BASE_URL", ANALYZER_BASE_URL)
ANONYMIZER_BASE_URL = os.environ.get("ANONYMIZER_BASE_URL", ANONYMIZER_BASE_URL)


def anonymize(data):
    response = requests.post(
        f"{ANONYMIZER_BASE_URL}/anonymize", data=data, headers=DEFAULT_HEADERS
    )
    return response.status_code, response.content


def anonymizers():
    response = requests.get(
        f"{ANONYMIZER_BASE_URL}/anonymizers", headers=DEFAULT_HEADERS
    )
    return response.status_code, response.content


def analyze(data):
    response = requests.post(
        f"{ANALYZER_BASE_URL}/analyze", data=data, headers=DEFAULT_HEADERS
    )
    return response.status_code, response.content


def analyzer_supported_entities(data):
    response = requests.get(
        f"{ANALYZER_BASE_URL}/supportedentities?{data}", headers=DEFAULT_HEADERS
    )
    return response.status_code, response.content
