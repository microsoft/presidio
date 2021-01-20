import json
import os

import app


def test_anonymize_api_works_properly():
    json_path = os.path.dirname(__file__) + "/resources/payload.json"
    with open(json_path) as json_file:
        content = json.load(json_file)
    tester = app.app.test_client()
    resp = tester.post("/anonymize", json=content)
    assert resp.status == "200 OK"
