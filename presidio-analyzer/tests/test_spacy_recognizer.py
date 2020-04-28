import pytest

from tests import assert_result_within_score_range


@pytest.fixture(scope="module")
def entities():
    return ["PERSON", "DATE_TIME"]


@pytest.fixture(scope="module")
def nlp_engine(nlp_engines):
    return nlp_engines["spacy_en"]


@pytest.fixture(scope="module")
def nlp_recognizer(nlp_recognizers):
    return nlp_recognizers["spacy"]


def prepare_and_analyze(nlp, recognizer, text, ents):
    nlp_artifacts = nlp.process_text(text, "en")
    results = recognizer.analyze(text, ents, nlp_artifacts)
    return results


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, entity_num",
    [
        # Test PERSON entity
        ("my name is Dan", 1, ((11, 14),), 0),
        ("Dan Tailor", 1, ((0, 10),), 0),
        ("John Oliver is a comedian.", 1, ((0, 11),), 0),
        ("Richard Milhous Nixon", 1, ((0, 21),), 0),
        ("Richard M. Nixon", 1, ((0, 16),), 0),
        ("Dan May has a bank account.", 1, ((0, 7),), 0),
        ("Mr. May", 1, ((4, 7),), 0),
        ("They call me Mr. May", 1, ((17, 20),), 0),
        # Test DATE_TIME Entity
        ("1972", 1, ((0, 4),), 1),
        ("I bought my car in 1972", 1, ((19, 23),), 1),
        ("I bought my car in May", 1, ((19, 22),), 1),
        ("May 1st", 1, ((0, 7),), 1),
        ("May 1st, 1977", 1, ((0, 13),), 1),
        ("I bought my car on May 1st, 1977", 1, ((19, 32),), 1),
    ],
)
def test_all_spacy(
    text,
    expected_len,
    expected_positions,
    entity_num,
    nlp_engine,
    nlp_recognizer,
    entities,
    ner_strength,
    max_score,
):
    results = prepare_and_analyze(nlp_engine, nlp_recognizer, text, entities)
    assert len(results) == expected_len
    entity_to_check = entities[entity_num]
    for res, (st_pos, fn_pos) in zip(results, expected_positions):
        assert_result_within_score_range(
            res, entity_to_check, st_pos, fn_pos, ner_strength, max_score
        )


def test_person_full_name_complex(nlp_engine, nlp_recognizer, entities):
    text = "Richard (Rick) C. Henderson"
    results = prepare_and_analyze(nlp_engine, nlp_recognizer, text, entities)

    assert len(results) > 0

    # check that most of the text is covered
    covered_text = ""
    for result in results:
        sl = slice(result.start, result.end)
        covered_text += text[sl]

    assert len(text) - len(covered_text) < 5
