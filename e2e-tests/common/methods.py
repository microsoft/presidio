import os
from typing import Dict

import requests

from common.constants import ANONYMIZER_BASE_URL, ANALYZER_BASE_URL, \
    IMAGE_REDACTOR_BASE_URL

DEFAULT_HEADERS = {"Content-Type": "application/json"}
MULTIPART_HEADERS = {"Content-Type": "multipart/form-data"}
ANALYZER_BASE_URL = os.environ.get("ANALYZER_BASE_URL", ANALYZER_BASE_URL)
ANONYMIZER_BASE_URL = os.environ.get("ANONYMIZER_BASE_URL", ANONYMIZER_BASE_URL)
IMAGE_REDACTOR_BASE_URL = os.environ.get("IMAGE_REDACTOR_BASE_URL",
                                         IMAGE_REDACTOR_BASE_URL)


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


def image_redactor(file_name: str, color_fill):
    multipart_form_data = (
        ('image', open(f"../resources/{file_name}", 'rb')),
        ('color_fill', color_fill),
    )
    response = requests.post(
        f"{ANALYZER_BASE_URL}/redact", data=multipart_form_data,
        headers=MULTIPART_HEADERS
    )
    return response.status_code, response.content
