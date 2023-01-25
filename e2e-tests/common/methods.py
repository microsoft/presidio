import base64
import json
import os

import requests

from common.constants import (
    ANONYMIZER_BASE_URL,
    ANALYZER_BASE_URL,
    IMAGE_REDACTOR_BASE_URL,
)

DEFAULT_HEADERS = {"Content-Type": "application/json"}
MULTIPART_HEADERS = {"Content-Type": "multipart/form-data"}
ANALYZER_BASE_URL = os.environ.get("ANALYZER_BASE_URL", ANALYZER_BASE_URL)
ANONYMIZER_BASE_URL = os.environ.get("ANONYMIZER_BASE_URL", ANONYMIZER_BASE_URL)
IMAGE_REDACTOR_BASE_URL = os.environ.get(
    "IMAGE_REDACTOR_BASE_URL", IMAGE_REDACTOR_BASE_URL
)


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


def redact(file, color_fill=None, json_payload=False):
    payload = __get_redact_payload(color_fill)
    if json_payload:
        json_string = '{"image": "' + base64.b64encode(file.read()).decode("utf-8") + '"}'
        response = requests.post(
            f"{IMAGE_REDACTOR_BASE_URL}/redact", json=json.loads(json_string), headers=DEFAULT_HEADERS
        )
    else:
        response = requests.post(
        f"{IMAGE_REDACTOR_BASE_URL}/redact", files=__get_multipart_form_data(file), data=payload)
    return response


def deanonymize(data):
    response = requests.post(
        f"{ANONYMIZER_BASE_URL}/deanonymize", data=data, headers=DEFAULT_HEADERS
    )
    return response.status_code, response.content


def __get_redact_payload(color_fill):
    payload = {}
    if color_fill:
        payload = {"data": "{'color_fill':'" + str(color_fill) + "'}"}
    return payload


def __get_multipart_form_data(file):
    multipart_form_data = {}
    if file:
        multipart_form_data = {
            "image": (file.name, file, "multipart/form-data"),
        }
    return multipart_form_data
