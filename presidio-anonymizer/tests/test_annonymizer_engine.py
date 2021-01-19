import json
import os

from presidio_anonymizer.domain import AnonymizerRequest
from presidio_anonymizer import AnonymizerEngine


def test_analyzer_results_sorted_set():
    json_path = os.path.dirname(__file__) + "/resources/dup_payload.json"
    with open(json_path) as json_file:
        content = json.load(json_file)
        data = AnonymizerRequest.validate_and_convert(content)
        text = AnonymizerEngine(data).anonymize()
        assert text == 'hello world, my name is <FULL_NAME>. ' \
                       'My number is: <PHONE_NUMBER>'
