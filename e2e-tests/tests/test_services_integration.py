import pytest

from common.methods import analyzer_supported_entities


# TODO: [ADO-2763] Stub, remove and replace with real integration scenarios
@pytest.mark.integration
def test_given_a_correct_input_for_supported_entities_then_expect_a_correct_response():
    language_query_parameter = "language=en"

    response_status, response_content = analyzer_supported_entities(
        language_query_parameter
    )

    assert response_status == 200

