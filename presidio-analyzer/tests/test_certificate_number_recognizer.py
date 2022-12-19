import pytest

from tests import assert_result
from presidio_analyzer.predefined_recognizers.medical_license_recognizer import MedicalLicenseRecognizer


@pytest.fixture(scope="module")
def cc_recognizer():
    return MedicalLicenseRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["MEDICAL_LICENSE"]


@pytest.mark.parametrize(
    "text, expected_len, expected_scores, expected_res",
    [
        # fmt: off
        ("GL0285191 EU4488929", 2, (), ((0, 9),(10,19),),),
        ("K92993548", 1, (), ((0, 9),),),
        ("my certificate number is: BB1388568", 1, (), ((26,35),),),
        ("The DEA number is  BG8207031", 0, (), (),),
        ("123 456\n789", 0, (), (),),
        # fmt: on
    ],
)
def test_when_all_medical_licence_number_then_succeed(
    text,
    expected_len,
    expected_scores,
    expected_res,
    cc_recognizer,
    entities,
    max_score,
):
    results = cc_recognizer.analyze(text, entities)
    assert len(results) == expected_len
    for res, expected_score in zip(results, expected_scores):
        assert res.score == expected_score
    for res, (start, end) in zip(results, expected_res):
        assert_result(res, entities[0], start, end, max_score)
