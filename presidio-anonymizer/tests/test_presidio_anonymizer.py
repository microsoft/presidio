#!/usr/bin/env python
"""Anonymizer routes tests."""
import api


def test_anonymize():
    """
    Test anonymize method.

    :return:
    """
    tester = api.app.test_client()
    resp = tester.post("/anonymize", json={"hello": 1, "world": "what?"})
    assert resp.json == {"hello": 1, "world": "what?"}
