import pytest

from tests import assert_result
from presidio_analyzer.predefined_recognizers import InVehicleRegistrationRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return InVehicleRegistrationRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["IN_VEHICLE_REGISTRATION"]


@pytest.mark.parametrize(
    "text, expected_len, expected_position, expected_score",
    [
        # fmt: off
        ("KA53ME3456", 1, (0, 10), 1),
        ("KA99ME3456", 1, (0, 10), 0.50),
        ("MN2412", 1, (0, 6), 0.01),
        ("MCX1243", 1, (0, 7), 0.2),
        ("I15432", 1, (0, 6), 0.01),
        ("ABNE123456", 0, (), (),),
        ("My Bike's registration number is OD02BA2341 with a lot of text beyond",
         1, (33, 43), 1),
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
    print("Results")
    print(results)

    assert len(results) == expected_len
    if results:
        assert_result(
            results[0],
            entities[0],
            expected_position[0],
            expected_position[1],
            expected_score,
        )
