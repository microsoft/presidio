error = 0.00001


def __assert_result_without_score(
    result, expected_entity_type, expected_start, expected_end
):
    assert result.entity_type == expected_entity_type
    assert result.start == expected_start
    assert result.end == expected_end


def assert_result(
    result, expected_entity_type, expected_start, expected_end, expected_score
):
    __assert_result_without_score(
        result, expected_entity_type, expected_start, expected_end
    )
    assert result.score == expected_score


def assert_result_within_score_range(
    result,
    expected_entity_type,
    expected_start,
    expected_end,
    expected_score_min,
    expected_score_max,
):
    __assert_result_without_score(
        result, expected_entity_type, expected_start, expected_end
    )
    min_score = max(0, expected_score_min - error)
    max_score = min(1, expected_score_max + error)
    assert result.score >= min_score and result.score <= max_score
