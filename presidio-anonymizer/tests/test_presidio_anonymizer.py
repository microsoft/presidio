from app import app


def test_anonymize():
    tester = app.test_client()
    resp = tester.post("/anonymize", json={"hello": 1, "world": "what?"})
    assert resp.json == {"hello": 1, "world": "what?"}
