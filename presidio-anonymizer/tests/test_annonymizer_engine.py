import json
import os

from presidio_anonymizer.entities import AnonymizerEngineRequest

from presidio_anonymizer import AnonymizerEngine


def test_engine_result():
    json_path = os.path.dirname(__file__) + "/resources/dup_payload.json"
    with open(json_path) as json_file:
        content = json.load(json_file)
        data = AnonymizerEngineRequest(content)
        text = AnonymizerEngine().anonymize(data)
        assert text == 'hello world, my name is <FULL_NAME>. ' \
                       'My number is: <PHONE_NUMBER>'
