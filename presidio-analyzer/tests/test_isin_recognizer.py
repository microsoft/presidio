import pytest

from tests import assert_result
from presidio_analyzer.predefined_recognizers import IsinRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return IsinRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["ISIN_CODE"]


@pytest.mark.parametrize(
    "text, expected_len, expected_position, expected_score",
    [
        # fmt: off
        ("IL0011762056", 1, (0, 12), 0.85),
        ("ZZ12345ABCD1", 1, (0, 12), 0.01),
        ("US0378331005", 1, (0, 12), 0.85),
        ("KR7000830000", 1, (0, 12), 0.85),
        ("IL0006290147", 1, (0, 12), 0.85),
        ("JP3967200001", 1, (0, 12), 0.85),
        ("ARDEUT110061", 1, (0, 12), 0.85),
        ("BRBOEIBDR003", 1, (0, 12), 0.85),
        ("KYG017171003", 1, (0, 12), 0.85),
        ("SG1T75931496", 1, (0, 12), 0.85),
        ("GB00B16PRC61", 1, (0, 12), 0.85),
        ("DE0007236101", 1, (0, 12), 0.85),
        ("XS1636274265", 1, (0, 12), 0.01),  # exception to XS as a country code
        ("INF740KA1BM0", 1, (0, 12), 0.85),
        ("INE732I01013", 1, (0, 12), 0.85),
        ("ABNE123456", 0, (), (),),
        ("My Listed Company's stock trades with ISIN number SA14TG012N13 with a lot of "
         "text beyond the actual value",
         1, (50, 62), 0.01),
        # fmt: on
    ],
)
def test_when_regn_in_text_then_all_regns_found(
    text,
    expected_len,
    expected_position,
    expected_score,
    recognizer,
    entities,
):
    results = recognizer.analyze(text, entities)

    assert len(results) == expected_len
    if results:
        assert_result(
            results[0],
            entities[0],
            expected_position[0],
            expected_position[1],
            expected_score,
        )
