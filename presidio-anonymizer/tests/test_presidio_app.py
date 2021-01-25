import json
import os

from app import Server


def test_anonymize_api_works_properly():
    json_path = os.path.dirname(__file__) + "/resources/payload.json"
    with open(json_path) as json_file:
        content = json.load(json_file)
    tester = Server().app.test_client()
    resp = tester.post("/anonymize", json=content)
    assert resp.data.decode() == 'hello world, my name is ANONYMIZED. My number is: '
    assert resp.status == "200 OK"


def test_anonymize_api_fails_on_invalid_value_of_text():
    json_path = os.path.dirname(__file__) + "/resources/payload.json"
    with open(json_path) as json_file:
        content = json.load(json_file)
        content["text"] = ""
    tester = Server().app.test_client()
    resp = tester.post("/anonymize", json=content)
    assert resp.data.decode() == "Invalid input, text can not be empty"
    assert resp.status == '422 UNPROCESSABLE ENTITY'
