import json
import os

from presidio_anonymizer.entities import AnonymizerRequest

from presidio_anonymizer import AnonymizerEngine


def test_engine_successful_result():
    json_path = os.path.dirname(__file__) + "/resources/dup_payload.json"
    with open(json_path) as json_file:
        content = json.load(json_file)
        data = AnonymizerRequest(content)
        text = AnonymizerEngine().anonymize(data)
        assert text == 'hello world, my name is <FULL_NAME>. ' \
                       'My number is: <PHONE_NUMBER>'
