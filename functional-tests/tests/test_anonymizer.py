from common.methods import anonymize


def test_anonymize():
    request_body = {"key": "value"}

    response_status, response_content = anonymize(request_body)

    assert response_status == 200
    assert response_content == {"key": "value"}
