import json

import pytest

from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import AnonymizerRequest
from tests.integration.file_utils import get_scenario_file_content


@pytest.mark.parametrize(
    "anonymize_scenario",
    [
        # "mask_name_phone_number",
        # "mask_phone_number_with_bad_masking_char",
        # "redact_and_replace",
        "replace_with_intersecting_entities",
        # "hash_md5",
        # "hash_sha256",
        # "hash_sha512",
        # "hash_sha256_default",
    ],
)
def test_when_anonymize_called_with_multiple_scenarios_then_expected_results_returned(
        anonymize_scenario,
):
    anonymizer_request_dict = json.loads(
        get_scenario_file_content("anonymize", f"{anonymize_scenario}.in.json")
    )
    expected_anonymize_result = json.loads(
        get_scenario_file_content("anonymize", f"{anonymize_scenario}.out.json")
    )
    engine = AnonymizerEngine()
    anonymizer_request = AnonymizerRequest(
        anonymizer_request_dict
    )

    try:
        actual_anonymize_result = engine.anonymize(anonymizer_request_dict.get("text"),
                                                   anonymizer_request)
    except Exception as e:
        actual_anonymize_result = str(e)

    assert actual_anonymize_result == expected_anonymize_result
