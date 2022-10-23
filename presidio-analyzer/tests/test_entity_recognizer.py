from presidio_analyzer import EntityRecognizer, RecognizerResult, AnalysisExplanation


def test_when_to_dict_then_return_correct_dictionary():
    ent_recognizer = EntityRecognizer(["ENTITY"])
    entity_rec_dict = ent_recognizer.to_dict()

    assert entity_rec_dict is not None
    assert entity_rec_dict["supported_entities"] == ["ENTITY"]
    assert entity_rec_dict["supported_language"] == "en"


def test_when_from_dict_then_returns_instance():
    ent_rec_dict = {"supported_entities": ["A", "B", "C"], "supported_language": "he"}
    entity_rec = EntityRecognizer.from_dict(ent_rec_dict)

    assert entity_rec.supported_entities == ["A", "B", "C"]
    assert entity_rec.supported_language == "he"
    assert entity_rec.version == "0.0.1"


def test_when_remove_duplicates_duplicates_removed():
    # test same result with different score will return only the highest
    arr = [
        RecognizerResult(
            start=0,
            end=5,
            score=0.1,
            entity_type="x",
            analysis_explanation=AnalysisExplanation(
                recognizer="test",
                original_score=0,
                pattern_name="test",
                pattern="test",
                validation_result=None,
            ),
        ),
        RecognizerResult(
            start=0,
            end=5,
            score=0.5,
            entity_type="x",
            analysis_explanation=AnalysisExplanation(
                recognizer="test",
                original_score=0,
                pattern_name="test",
                pattern="test",
                validation_result=None,
            ),
        ),
    ]
    results = EntityRecognizer.remove_duplicates(arr)
    assert len(results) == 1
    assert results[0].score == 0.5


def test_when_remove_duplicates_different_then_entity_not_removed():
    # test same result with different score will return only the highest
    arr = [
        RecognizerResult(
            start=0,
            end=5,
            score=0.1,
            entity_type="x",
            analysis_explanation=AnalysisExplanation(
                recognizer="test",
                original_score=0,
                pattern_name="test",
                pattern="test",
                validation_result=None,
            ),
        ),
        RecognizerResult(
            start=0,
            end=5,
            score=0.5,
            entity_type="y",
            analysis_explanation=AnalysisExplanation(
                recognizer="test",
                original_score=0,
                pattern_name="test",
                pattern="test",
                validation_result=None,
            ),
        ),
    ]
    results = EntityRecognizer.remove_duplicates(arr)
    assert len(results) == 2


def test_when_remove_duplicates_contained_shorter_length_results_removed():
    arr = [
        RecognizerResult(
            start=0,
            end=10,
            score=0.5,
            entity_type="x",
            analysis_explanation=AnalysisExplanation(
                recognizer="test",
                original_score=0,
                pattern_name="test",
                pattern="test",
                validation_result=None,
            ),
        ),
        RecognizerResult(
            start=0,
            end=5,
            score=0.5,
            entity_type="x",
            analysis_explanation=AnalysisExplanation(
                recognizer="test",
                original_score=0,
                pattern_name="test",
                pattern="test",
                validation_result=None,
            ),
        ),
    ]
    results = EntityRecognizer.remove_duplicates(arr)
    assert len(results) == 1
