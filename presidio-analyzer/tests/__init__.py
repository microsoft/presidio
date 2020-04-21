import os
import sys

from presidio_analyzer.nlp_engine import SpacyNlpEngine

sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))) + "/tests")

from .assertions import assert_result, assert_result_within_score_range

print("Creating tests SpacyNlpEngine which starts the spaCy model")
TESTS_NLP_ENGINE = SpacyNlpEngine({"en": "en_core_web_lg"})
