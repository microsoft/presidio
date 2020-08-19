import os
import pytest

from presidio_analyzer import PatternRecognizer, Pattern
from presidio_analyzer.predefined_recognizers import (
    AbaRoutingRecognizer,
    # CreditCardRecognizer,
    UsPhoneRecognizer,
    # DomainRecognizer,
    UsItinRecognizer,
    UsLicenseRecognizer,
    UsBankRecognizer,
    UsPassportRecognizer,
    IpRecognizer,
    UsSsnRecognizer,
    SgFinRecognizer,
)
from presidio_analyzer.nlp_engine import NlpArtifacts


@pytest.fixture(scope="module")
def recognizers():
    rec_map = {
        "IP_ADDRESS": IpRecognizer(),
        "US_SSN": UsSsnRecognizer(),
        "PHONE_NUMBER": UsPhoneRecognizer(),
        "ABA_ROUTING_NUMBER": AbaRoutingRecognizer(),
        "US_ITIN": UsItinRecognizer(),
        "US_DRIVER_LICENSE": UsLicenseRecognizer(),
        "US_BANK_NUMBER": UsBankRecognizer(),
        "US_PASSPORT": UsPassportRecognizer(),
        "FIN": SgFinRecognizer(),
    }
    return rec_map


@pytest.fixture(scope="module")
def nlp_engine(nlp_engines):
    return nlp_engines["spacy_en"]


@pytest.fixture(scope="module")
def dataset(recognizers):
    """ Loads up a group of sentences with relevant context words and creates
        a list of tuples of the sentence, a recognizer and entity types.
    """

    data_path = os.path.dirname(__file__) + "/data/context_sentences_tests.txt"
    with open(data_path, "r") as f:
        # get non-empty lines without comments
        lines = [l.strip() for l in f if l[0] != "#" and l.strip()]

    test_items = []
    for i in range(0, len(lines), 2):
        entity_type = lines[i].strip()
        item = lines[i + 1].strip()
        recognizer = recognizers.get(entity_type, None)
        if not recognizer:
            # will fail the test in its turn
            raise ValueError(f"bad entity type {entity_type}")

        test_items.append((item, recognizer, [entity_type]))
    # Currently we have 28 sentences, this is a sanity check
    if not len(test_items) == 28:
        raise ValueError(f"expected 28 context sentences but found {len(test_items)}")

    yield test_items


@pytest.fixture(scope="function")
def mock_nlp_artifacts():
    return NlpArtifacts([], [], [], [], None, "en")


def test_text_with_context_improves_score(dataset, nlp_engine, mock_nlp_artifacts):
    for item in dataset:
        text, recognizer, entities = item
        nlp_artifacts = nlp_engine.process_text(text, "en")
        results_without_context = recognizer.analyze(text, entities, mock_nlp_artifacts)
        results_with_context = recognizer.analyze(text, entities, nlp_artifacts)

        assert len(results_without_context) == len(results_with_context)
        for res_wo, res_w in zip(results_without_context, results_with_context):
            if res_wo.score != 1.0:
                assert res_wo.score < res_w.score
            else:
                assert res_wo.score <= res_w.score


def test_context_custom_recognizer(nlp_engine, mock_nlp_artifacts):
    """This test checks that a custom recognizer is also enhanced by context.
       However this test also verifies a specific case in which the pattern also
       includes a preceeding space (' rocket'). This in turn cause for a misalignment
       between the tokens and the regex match (the token will be just 'rocket').
       This misalignment is handled in order to find the correct context window.
    """
    rocket_recognizer = PatternRecognizer(
        supported_entity="ROCKET",
        name="rocketrecognizer",
        context=["cool"],
        patterns=[Pattern("rocketpattern", r"\\s+(rocket)", 0.3)],
    )
    text = "hi, this is a cool ROCKET"
    recognizer = rocket_recognizer
    entities = ["ROCKET"]
    nlp_artifacts = nlp_engine.process_text(text, "en")
    results_without_context = recognizer.analyze(text, entities, mock_nlp_artifacts)
    results_with_context = recognizer.analyze(text, entities, nlp_artifacts)
    assert len(results_without_context) == len(results_with_context)
    for res_wo, res_w in zip(results_without_context, results_with_context):
        assert res_wo.score < res_w.score
