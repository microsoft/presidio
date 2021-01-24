import pytest
from common.methods import anonymize


@pytest.mark.api
def test_anonymize():
    request_body = {
        "text": "hello world, my name is Jane Doe. My number is: 034453334",
        "transformations": {"DEFAULT": {"type": "replace", "new_value": "ANONYMIZED"}},
        "analyzer_results": [
            {"start": 24, "end": 32, "score": 0.8, "entity_type": "NAME"}
        ],
    }

    response_status, response_content = anonymize(request_body)

    assert response_status == 200
    assert response_content == "hello world, my name is <NAME>. My number is: 034453334"
