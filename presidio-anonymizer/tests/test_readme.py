def test_readme():
    # Tests that the readme code snippet doesn't fail
    from presidio_anonymizer import AnonymizerEngine
    from presidio_anonymizer.entities import RecognizerResult, OperatorConfig

    # Initialize the engine with logger.
    engine = AnonymizerEngine()

    # Invoke the anonymize function with the text,
    # analyzer results (potentially coming from presidio-analyzer) and
    # Operators to get the anonymization output:
    result = engine.anonymize(
        text="My name is Bond, James Bond",
        analyzer_results=[
            RecognizerResult(entity_type="PERSON", start=11, end=15, score=0.8),
            RecognizerResult(entity_type="PERSON", start=17, end=27, score=0.8),
        ],
        operators={"PERSON": OperatorConfig("replace", {"new_value": "BIP"})},
    )

    print(result)


def test_readme_decrypt():
    from presidio_anonymizer import DeanonymizeEngine
    from presidio_anonymizer.entities import OperatorResult, OperatorConfig

    # Initialize the engine with logger.
    engine = DeanonymizeEngine()

    # Invoke the deanonymize function with the text, anonymizer results and
    # Operators to define the deanonymization type.
    result = engine.deanonymize(
        text="My name is S184CMt9Drj7QaKQ21JTrpYzghnboTF9pn/neN8JME0=",
        entities=[
            OperatorResult(start=11, end=55, entity_type="PERSON"),
        ],
        operators={"DEFAULT": OperatorConfig("decrypt", {"key": "WmZq4t7w!z%C&F)J"})},
    )

    print(result)
