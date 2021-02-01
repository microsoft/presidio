import json

import pytest

from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import AnonymizerRequest
from tests.integration.file_utils import get_scenario_file_content


@pytest.mark.parametrize(
    "anonymize_scenario",
    [
        "mask_name_phone_number",
        "mask_phone_number_with_bad_masking_char",
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
    anonymizer_request = AnonymizerRequest(anonymizer_request_dict, engine.builtin_anonymizers)

    try:
        actual_anonymize_result = engine.anonymize(anonymizer_request)
    except Exception as e:
        actual_anonymize_result = str(e)

    assert actual_anonymize_result == expected_anonymize_result
