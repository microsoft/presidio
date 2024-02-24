import pytest

from tests import assert_result
from presidio_analyzer.predefined_recognizers import CfiRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return CfiRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["CFI_CODE"]


@pytest.mark.parametrize(
    "text, expected_len, expected_position, expected_score",
    [
        # fmt: off
        ("ESVUFA", 1, (0, 6), 0.5),
        ("JFTXFP", 1, (0, 6), 1.0),
        ("JFTXFN", 1, (0, 6), 1.0),
        ("ESVUFR", 1, (0, 6), 1.0),
        ("ABNE123456", 0, (), (),),
        ("OCXFXS", 1, (0, 6), 0.5),
        ("DZXBAC", 1, (0, 6), 0.10),
        ("ABCDEF", 1, (0, 6), 0.05),
        ("MMRXXX", 1, (0, 6), 1.0),
        ("TBEXXX", 1, (0, 6), 1.0),
        ("NABHRT", 1, (0, 6), 0.05),
        # fmt: on
    ],
)
def test_when_cfi_in_text_then_all_cfis_found(
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
