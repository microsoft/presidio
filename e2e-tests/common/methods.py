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
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, "..", "resources", file_name)
    multipart_form_data = {
        "image": (file_name, open(file_path, "rb"), "multipart/form-data"),
    }
    payload = {}
    if color_fill:
        payload = {"data": "{'color_fill':'" + str(color_fill) + "'}"}
    response = requests.post(f"{IMAGE_REDACTOR_BASE_URL}/redact",
                             files=multipart_form_data, data=payload
                             )
    return response.status_code, response.content
