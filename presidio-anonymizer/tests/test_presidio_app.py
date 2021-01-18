import json

import app


def test_anonymize():
    with open("resources/payload.json") as json_file:
        content = json.load(json_file)
    tester = app.app.test_client()
    resp = tester.post("/anonymize", json=content)
    assert resp.status == "200 OK"
