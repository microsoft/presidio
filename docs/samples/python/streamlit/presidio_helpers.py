"""
Helper methods for the Presidio Streamlit app
"""
from typing import List, Optional

import spacy
import streamlit as st
from presidio_analyzer import AnalyzerEngine, RecognizerResult, RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

from flair_recognizer import FlairRecognizer
from openai_fake_data_generator import (
    set_openai_key,
    call_completion_model,
    create_prompt,
)
from transformers_rec import (
    STANFORD_COFIGURATION,
    TransformersRecognizer,
    BERT_DEID_CONFIGURATION,
)


@st.cache_resource
def analyzer_engine(model_path: str):
    """Return AnalyzerEngine.

    :param model_path: Which model to use for NER:
        "StanfordAIMI/stanford-deidentifier-base",
        "obi/deid_roberta_i2b2",
        "en_core_web_lg"
    """

    registry = RecognizerRegistry()
    registry.load_predefined_recognizers()

    # Set up NLP Engine according to the model of choice
    if model_path == "en_core_web_lg":
        if not spacy.util.is_package("en_core_web_lg"):
            spacy.cli.download("en_core_web_lg")
        nlp_configuration = {
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "en", "model_name": "en_core_web_lg"}],
        }
    elif model_path == "flair/ner-english-large":
        flair_recognizer = FlairRecognizer()
        nlp_configuration = {
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
        }
        registry.add_recognizer(flair_recognizer)
        registry.remove_recognizer("SpacyRecognizer")
    else:
        if not spacy.util.is_package("en_core_web_sm"):
            spacy.cli.download("en_core_web_sm")
        # Using a small spaCy model + a HF NER model
        transformers_recognizer = TransformersRecognizer(model_path=model_path)
        registry.remove_recognizer("SpacyRecognizer")
        if model_path == "StanfordAIMI/stanford-deidentifier-base":
            transformers_recognizer.load_transformer(**STANFORD_COFIGURATION)
        elif model_path == "obi/deid_roberta_i2b2":
            transformers_recognizer.load_transformer(**BERT_DEID_CONFIGURATION)

        # Use small spaCy model, no need for both spacy and HF models
        # The transformers model is used here as a recognizer, not as an NlpEngine
        nlp_configuration = {
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
        }

        registry.add_recognizer(transformers_recognizer)

    nlp_engine = NlpEngineProvider(nlp_configuration=nlp_configuration).create_engine()

    analyzer = AnalyzerEngine(nlp_engine=nlp_engine, registry=registry)
    return analyzer


@st.cache_resource
def anonymizer_engine():
    """Return AnonymizerEngine."""
    return AnonymizerEngine()


@st.cache_data
def get_supported_entities(st_model: str):
    """Return supported entities from the Analyzer Engine."""
    return analyzer_engine(st_model).get_supported_entities()


@st.cache_data
def analyze(st_model: str, **kwargs):
    """Analyze input using Analyzer engine and input arguments (kwargs)."""
    if "entities" not in kwargs or "All" in kwargs["entities"]:
        kwargs["entities"] = None
    return analyzer_engine(st_model).analyze(**kwargs)


def anonymize(
    text: str,
    operator: str,
    analyze_results: List[RecognizerResult],
    mask_char: Optional[str] = None,
    number_of_chars: Optional[str] = None,
    encrypt_key: Optional[str] = None,
):
    """Anonymize identified input using Presidio Anonymizer.

    :param text: Full text
    :param operator: Operator name
    :param mask_char: Mask char (for mask operator)
    :param number_of_chars: Number of characters to mask (for mask operator)
    :param encrypt_key: Encryption key (for encrypt operator)
    :param analyze_results: list of results from presidio analyzer engine
    """

    if operator == "mask":
        operator_config = {
            "type": "mask",
            "masking_char": mask_char,
            "chars_to_mask": number_of_chars,
            "from_end": False,
        }

    # Define operator config
    elif operator == "encrypt":
        operator_config = {"key": encrypt_key}
    elif operator == "highlight":
        operator_config = {"lambda": lambda x: x}
    else:
        operator_config = None

    # Change operator if needed as intermediate step
    if operator == "highlight":
        operator = "custom"
    elif operator == "synthesize":
        operator = "replace"
    else:
        operator = operator

    res = anonymizer_engine().anonymize(
        text,
        analyze_results,
        operators={"DEFAULT": OperatorConfig(operator, operator_config)},
    )
    return res


def annotate(text: str, analyze_results: List[RecognizerResult]):
    """Highlight the identified PII entities on the original text

    :param text: Full text
    :param analyze_results: list of results from presidio analyzer engine
    """
    tokens = []

    # Use the anonymizer to resolve overlaps
    results = anonymize(
        text=text,
        operator="highlight",
        analyze_results=analyze_results,
    )

    # sort by start index
    results = sorted(results.items, key=lambda x: x.start)
    for i, res in enumerate(results):
        if i == 0:
            tokens.append(text[: res.start])

        # append entity text and entity type
        tokens.append((text[res.start : res.end], res.entity_type))

        # if another entity coming i.e. we're not at the last results element, add text up to next entity
        if i != len(results) - 1:
            tokens.append(text[res.end : results[i + 1].start])
        # if no more entities coming, add all remaining text
        else:
            tokens.append(text[res.end :])
    return tokens


def create_fake_data(
    text: str,
    analyze_results: List[RecognizerResult],
    openai_key: str,
    openai_model_name: str,
):
    """Creates a synthetic version of the text using OpenAI APIs"""
    if not openai_key:
        return "Please provide your OpenAI key"
    results = anonymize(text=text, operator="replace", analyze_results=analyze_results)
    set_openai_key(openai_key)
    prompt = create_prompt(results.text)
    fake = call_openai_api(prompt, openai_model_name)
    return fake


@st.cache_data
def call_openai_api(prompt: str, openai_model_name: str) -> str:
    fake_data = call_completion_model(prompt, model=openai_model_name)
    return fake_data
