import pytest

from presidio_analyzer.nlp_engine import NLP_ENGINES
from presidio_analyzer.predefined_recognizers import NLP_RECOGNIZERS
from presidio_analyzer.entity_recognizer import EntityRecognizer


def pytest_addoption(parser):
    parser.addoption(
        "--runslow", action="store_true", default=False, help="run slow tests"
    )

def pytest_configure(config):
    config.addinivalue_line("markers", "slow: mark test as slow to run")
    config.addinivalue_line("markers", "skip_engine(nlp_engine): skip test for given nlp engine")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--runslow"):
        # --runslow given in cli: do not skip slow tests
        return
    skip_slow = pytest.mark.skip(reason="need --runslow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)

@pytest.fixture(scope="session")
def nlp_engines(request):
    available_engines = {}
    for name, engine_cls in NLP_ENGINES.items():
        print(f"======================================\n\n{name} | {engine_cls}")
        available_engines[f"{name}_en"] = engine_cls()
        if name == "spacy" and request.config.getoption("--runslow"):
            available_engines[f"{name}_en_core_web_lg"] = engine_cls({"en": "en_core_web_lg"})
    return available_engines

@pytest.fixture(autouse=True)
def skip_by_engine(request, nlp_engines):
    marker = request.node.get_closest_marker('skip_engine')
    if marker:
        marker_arg = marker.args[0]
        if marker_arg not in nlp_engines:
            pytest.skip(f"skipped on this engine: {marker_arg}")

@pytest.fixture(scope="session")
def nlp_recognizers():
    return {name: rec_cls() for name, rec_cls in NLP_RECOGNIZERS.items()}

@pytest.fixture(scope="session")
def max_score():
    return EntityRecognizer.MAX_SCORE 
