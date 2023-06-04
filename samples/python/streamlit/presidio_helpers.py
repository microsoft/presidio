"""
Helper methods for the Presidio Streamlit app
"""
from typing import List, Optional, Tuple
import logging
import streamlit as st
from presidio_analyzer import (
    AnalyzerEngine,
    RecognizerResult,
    RecognizerRegistry,
    PatternRecognizer,
    Pattern,
)
from presidio_analyzer.nlp_engine import NlpEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

from openai_fake_data_generator import (
    set_openai_params,
    call_completion_model,
    create_prompt,
    OpenAIParams,
)
from presidio_nlp_engine_config import (
    create_nlp_engine_with_spacy,
    create_nlp_engine_with_flair,
    create_nlp_engine_with_transformers,
    create_nlp_engine_with_azure_text_analytics,
)

logger = logging.getLogger("presidio-streamlit")


@st.cache_resource
def nlp_engine_and_registry(
    model_family: str,
    model_path: str,
    ta_key: Optional[str] = None,
    ta_endpoint: Optional[str] = None,
) -> Tuple[NlpEngine, RecognizerRegistry]:
    """Create the NLP Engine instance based on the requested model.
    :param model_family: Which model package to use for NER.
    :param model_path: Which model to use for NER. E.g.,
        "StanfordAIMI/stanford-deidentifier-base",
        "obi/deid_roberta_i2b2",
        "en_core_web_lg"
    :param ta_key: Key to the Text Analytics endpoint (only if model_path = "Azure Text Analytics")
    :param ta_endpoint: Endpoint of the Text Analytics instance (only if model_path = "Azure Text Analytics")
    """

    # Set up NLP Engine according to the model of choice
    if "spaCy" in model_family:
        return create_nlp_engine_with_spacy(model_path)
    elif "flair" in model_family:
        return create_nlp_engine_with_flair(model_path)
    elif "HuggingFace" in model_family:
        return create_nlp_engine_with_transformers(model_path)
    elif "Azure Text Analytics" in model_family:
        return create_nlp_engine_with_azure_text_analytics(ta_key, ta_endpoint)
    else:
        raise ValueError(f"Model family {model_family} not supported")


@st.cache_resource
def analyzer_engine(
    model_family: str,
    model_path: str,
    ta_key: Optional[str] = None,
    ta_endpoint: Optional[str] = None,
) -> AnalyzerEngine:
    """Create the NLP Engine instance based on the requested model.
    :param model_family: Which model package to use for NER.
    :param model_path: Which model to use for NER:
        "StanfordAIMI/stanford-deidentifier-base",
        "obi/deid_roberta_i2b2",
        "en_core_web_lg"
    :param ta_key: Key to the Text Analytics endpoint (only if model_path = "Azure Text Analytics")
    :param ta_endpoint: Endpoint of the Text Analytics instance (only if model_path = "Azure Text Analytics")
    """
    nlp_engine, registry = nlp_engine_and_registry(
        model_family, model_path, ta_key, ta_endpoint
    )
    analyzer = AnalyzerEngine(nlp_engine=nlp_engine, registry=registry)
    return analyzer


@st.cache_resource
def anonymizer_engine():
    """Return AnonymizerEngine."""
    return AnonymizerEngine()


@st.cache_data
def get_supported_entities(
    model_family: str, model_path: str, ta_key: str, ta_endpoint: str
):
    """Return supported entities from the Analyzer Engine."""
    return analyzer_engine(
        model_family, model_path, ta_key, ta_endpoint
    ).get_supported_entities() + ["GENERIC_PII"]


@st.cache_data
def analyze(
    model_family: str, model_path: str, ta_key: str, ta_endpoint: str, **kwargs
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

    return analyzer_engine(model_family, model_path, ta_key, ta_endpoint).analyze(
        **kwargs
    )


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
    set_openai_params(openai_params)
    prompt = create_prompt(results.text)
    print(f"Prompt: {prompt}")
    fake = call_openai_api(
        prompt=prompt,
        openai_model_name=openai_params.model,
        openai_deployment_name=openai_params.deployment_name,
    )
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
