from typing import Iterator


def test_simple_process_text(nlp_engine):

    nlp_artifacts = nlp_engine.process_text("simple text", language="en")
    assert len(nlp_artifacts.tokens) == 2
    assert not nlp_artifacts.entities
    assert nlp_artifacts.lemmas[0] == "simple"
    assert nlp_artifacts.lemmas[1] == "text"


def test_process_batch_strings(nlp_engine):

    nlp_artifacts_batch = nlp_engine.process_batch(
        ["simple text", "simple text"], language="en"
    )
    assert isinstance(nlp_artifacts_batch, Iterator)
    nlp_artifacts_batch = list(nlp_artifacts_batch)

    for text, nlp_artifacts in nlp_artifacts_batch:
        assert text == "simple text"
        assert len(nlp_artifacts.tokens) == 2
