import json
import os

from app import Server


def test_anonymize_api_works_properly():
    json_path = os.path.dirname(__file__) + "/resources/payload.json"
    with open(json_path) as json_file:
        content = json.load(json_file)
    tester = Server().app.test_client()
    resp = tester.post("/anonymize", json=content)
    assert resp.status == "200 OK"
