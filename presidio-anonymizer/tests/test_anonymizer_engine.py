from presidio_anonymizer import AnonymizerEngine


def test_given_request_anonymizers_return_list():
    engine = AnonymizerEngine()
    expected_list = ["fpe", "hash", "mask", "redact", "replace"]
    anon_list = engine.anonymizers()

    assert anon_list == expected_list
