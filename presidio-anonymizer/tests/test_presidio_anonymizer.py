#!/usr/bin/env python
import api


def test_anonymize():
    tester = api.app.test_client()
    resp = tester.post("/anonymize", json={"hello": 1, "world": "what?"})
    assert resp.json == {"hello": 1, "world": "what?"}
