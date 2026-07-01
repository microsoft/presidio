"""
Helper methods for the Presidio Streamlit app
"""

import logging
from typing import List, Optional

import streamlit as st
from openai_fake_data_generator import (
    OpenAIParams,
    call_completion_model,
    create_prompt,
)
from presidio_analyzer import (
    AnalyzerEngine,
    Pattern,
    PatternRecognizer,
    RecognizerResult,
)
from presidio_analyzer_config import create_analyzer_engine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

logger = logging.getLogger("presidio-streamlit")


@st.cache_resource
def analyzer_engine(
    model_family: str, model_path: str, config_yaml: Optional[str] = None
) -> AnalyzerEngine:
    """Create the AnalyzerEngine instance based on the requested model.

    The engine is built from the declarative YAML configuration in ``config/``
    (see ``presidio_analyzer_config.py``), or from ``config_yaml`` if provided
    (the in-app editor, enabled via ``ALLOW_CONFIG_EDIT``).

    :param model_family: Which model package to use for NER
        (spacy, stanza, gliner, flair, huggingface).
    :param model_path: Which model to use for NER. E.g.,
        "en_core_web_lg",
        "urchade/gliner_multi_pii-v1",
        "OpenMed/OpenMed-PII-GTEMed-Base-149M-v1".
    :param config_yaml: Optional raw YAML overriding the committed config file.
    """
    return create_analyzer_engine(model_family, model_path, config_yaml)


@st.cache_resource
def anonymizer_engine():
    """Return AnonymizerEngine."""
    return AnonymizerEngine()


@st.cache_data
def get_supported_entities(
    model_family: str, model_path: str, config_yaml: Optional[str] = None
):
    """Return supported entities from the Analyzer Engine."""
    return analyzer_engine(
        model_family, model_path, config_yaml
    ).get_supported_entities() + ["GENERIC_PII"]


@st.cache_data
def analyze(
    model_family: str, model_path: str, config_yaml: Optional[str] = None, **kwargs
):
    """Analyze input using Analyzer engine and input arguments (kwargs)."""
    if "entities" not in kwargs or "All" in kwargs["entities"]:
        kwargs["entities"] = None

    if "deny_list" in kwargs and kwargs["deny_list"] is not None:
        ad_hoc_recognizer = create_ad_hoc_deny_list_recognizer(kwargs["deny_list"])
        kwargs["ad_hoc_recognizers"] = [ad_hoc_recognizer] if ad_hoc_recognizer else []
        del kwargs["deny_list"]

    if "regex_params" in kwargs and len(kwargs["regex_params"]) > 0:
        ad_hoc_recognizer = create_ad_hoc_regex_recognizer(*kwargs["regex_params"])
        kwargs["ad_hoc_recognizers"] = [ad_hoc_recognizer] if ad_hoc_recognizer else []
        del kwargs["regex_params"]

    return analyzer_engine(model_family, model_path, config_yaml).analyze(**kwargs)


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
    openai_params: OpenAIParams,
):
    """Creates a synthetic version of the text using OpenAI APIs"""
    if not openai_params.openai_key:
        return "Please provide your OpenAI key"
    results = anonymize(text=text, operator="replace", analyze_results=analyze_results)
    prompt = create_prompt(results.text)
    print(f"Prompt: {prompt}")
    fake = call_completion_model(prompt=prompt, openai_params=openai_params)
    return fake


@st.cache_data
def call_openai_api(
    prompt: str, openai_model_name: str, openai_deployment_name: Optional[str] = None
) -> str:
    fake_data = call_completion_model(
        prompt, model=openai_model_name, deployment_id=openai_deployment_name
    )
    return fake_data


def create_ad_hoc_deny_list_recognizer(
    deny_list=Optional[List[str]],
) -> Optional[PatternRecognizer]:
    if not deny_list:
        return None

    deny_list_recognizer = PatternRecognizer(
        supported_entity="GENERIC_PII", deny_list=deny_list
    )
    return deny_list_recognizer


def create_ad_hoc_regex_recognizer(
    regex: str, entity_type: str, score: float, context: Optional[List[str]] = None
) -> Optional[PatternRecognizer]:
    if not regex:
        return None
    pattern = Pattern(name="Regex pattern", regex=regex, score=score)
    regex_recognizer = PatternRecognizer(
        supported_entity=entity_type, patterns=[pattern], context=context
    )
    return regex_recognizer
