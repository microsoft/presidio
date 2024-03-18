import pytest

from presidio_analyzer.predefined_recognizers.phone_recognizer import PhoneRecognizer
from tests import assert_result


@pytest.fixture(scope="module")
def recognizer():
    return PhoneRecognizer()



@pytest.mark.parametrize(
    "text, expected_len, entities, expected_positions, score",
    [
        # fmt: off
        ("My US number is (415) 555-0132, and my international one is +1 415 555 0132",
         2, ["PHONE_NUMBER", "PHONE_NUMBER"],
         ((16, 30), (60, 75),), 0.4),
        ("My Israeli number is 09-7625400", 1, ["PHONE_NUMBER"], ((21, 31), ), 0.4),
        ("_: (415)555-0132", 1, ["PHONE_NUMBER"], ((3, 16), ), 0.4),
        ("United States: (415)555-0132", 1, ["PHONE_NUMBER"], ((15, 28), ), 0.4),
        ("US: 415-555-0132", 1, ["PHONE_NUMBER"], ((4, 16), ), 0.4),  # 'us' stop word
        ("_: +55 11 98456 5666", 1, ["PHONE_NUMBER"], ((3, 20), ), 0.4),
        ("Brazil: +55 11 98456 5666", 1, ["PHONE_NUMBER"], ((8, 25), ), 0.4),
        ("BR: +55 11 98456 5666", 1, ["PHONE_NUMBER"], ((4, 21), ), 0.4),
        # fmt: on
    ],
)
def test_when_all_phones_then_succeed(
    spacy_nlp_engine,
    text,
    expected_len,
    entities,
    expected_positions,
    score,
    recognizer,
):
    nlp_artifacts = spacy_nlp_engine.process_text(text, "en")
    results = recognizer.analyze(text, entities, nlp_artifacts=nlp_artifacts)
    assert len(results) == expected_len
    for i, (res, (st_pos, fn_pos)) in enumerate(zip(results, expected_positions)):
        assert_result(res, entities[i], st_pos, fn_pos, score)


@pytest.mark.parametrize(
    "text, expected_len, entities, expected_positions, score, leniency",
    [
        # fmt: off
        ("My US number is (415) 555-0132, and my international one is415-555-0132",
         1, ["PHONE_NUMBER"], ((16, 30), ), 0.4, 1),
        ("My US number is (415) 555-0132, and my international one is415-555-0132",
         2, ["PHONE_NUMBER", "PHONE_NUMBER"], ((16, 30), (59, 71), ), 0.4, 0),

        ("My US number is (415) 555-0132, and my international one is 91-415-555-0132",
         1, ["PHONE_NUMBER"], ((16, 30), ), 0.4, 2),
        ("My US number is (415) 555-0132, and my international one is 91-415-555-0132",
         2, ["PHONE_NUMBER", "PHONE_NUMBER"], ((16, 30), (60, 75), ), 0.4, 1),

        ("My US number is (415) 555-0132, and my international one is +91 4155 550132",
         1, ["PHONE_NUMBER"], ((16, 30), ), 0.4, 3),
        ("My US number is (415) 555-0132, and my international one is +91 4155 550132",
         2, ["PHONE_NUMBER", "PHONE_NUMBER"], ((16, 30), (60, 75), ), 0.4, 2),

        ("My US number is (415) 555-0132, and my international one is +91 4155550132",
         2, ["PHONE_NUMBER", "PHONE_NUMBER"], ((16, 30), (60, 74), ), 0.4, 3),
        # fmt: on
    ],
)
def test_when_phone_with_leniency_then_succeed(
    spacy_nlp_engine,
    text,
    expected_len,
    entities,
    expected_positions,
    score,
    leniency,
):
    nlp_artifacts = spacy_nlp_engine.process_text(text, "en")
    recognizer = PhoneRecognizer(leniency=leniency)
    results = recognizer.analyze(text, entities, nlp_artifacts=nlp_artifacts)
    assert len(results) == expected_len
    for i, (res, (st_pos, fn_pos)) in enumerate(zip(results, expected_positions)):
        assert_result(res, entities[i], st_pos, fn_pos, score)


def test_get_analysis_explanation():
    phone_recognizer = PhoneRecognizer()
    test_region = "US"
    explanation = phone_recognizer._get_analysis_explanation(test_region)
    assert explanation.recognizer == "PhoneRecognizer"