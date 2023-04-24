"""Streamlit app for Presidio."""
import os
from json import JSONEncoder

import pandas as pd
import streamlit as st
from annotated_text import annotated_text

from presidio_helpers import (
    get_supported_entities,
    analyze,
    anonymize,
    annotate,
    create_fake_data,
    analyzer_engine,
)

st.set_page_config(page_title="Presidio demo", layout="wide")

# Sidebar
st.sidebar.header(
    """
PII De-Identification with Microsoft Presidio
"""
)

st.sidebar.info(
    "Presidio is an open source customizable framework for PII detection and de-identification\n"
    "[Code](https://aka.ms/presidio) | "
    "[Tutorial](https://microsoft.github.io/presidio/tutorial/) | "
    "[Installation](https://microsoft.github.io/presidio/installation/) | "
    "[FAQ](https://microsoft.github.io/presidio/faq/)",
    icon="ℹ️",
)

st.sidebar.markdown(
    "[![Pypi Downloads](https://img.shields.io/pypi/dm/presidio-analyzer.svg)](https://img.shields.io/pypi/dm/presidio-analyzer.svg)" # noqa
    "[![MIT license](https://img.shields.io/badge/license-MIT-brightgreen.svg)](https://opensource.org/licenses/MIT)"
    "![GitHub Repo stars](https://img.shields.io/github/stars/microsoft/presidio?style=social)"
)

st_model = st.sidebar.selectbox(
    "NER model for PII detection",
    [
        "StanfordAIMI/stanford-deidentifier-base",
        "obi/deid_roberta_i2b2",
        "flair/ner-english-large",
        "en_core_web_lg",
    ],
    index=1,
    help="""
    Select which Named Entity Recognition (NER) model to use for PII detection, in parallel to rule-based recognizers.
    Presidio supports multiple NER packages off-the-shelf, such as spaCy, Huggingface, Stanza and Flair.
    """,
)
st.sidebar.markdown("> Note: Models might take some time to download. ")

st_operator = st.sidebar.selectbox(
    "De-identification approach",
    ["redact", "replace", "synthesize", "highlight", "mask", "hash", "encrypt"],
    index=1,
    help="""
    Select which manipulation to the text is requested after PII has been identified.\n
    - Redact: Completely remove the PII text\n
    - Replace: Replace the PII text with a constant, e.g. <PERSON>\n
    - Synthesize: Replace with fake values (requires an OpenAI key)\n
    - Highlight: Shows the original text with PII highlighted in colors\n
    - Mask: Replaces a requested number of characters with an asterisk (or other mask character)\n
    - Hash: Replaces with the hash of the PII string\n
    - Encrypt: Replaces with an AES encryption of the PII string, allowing the process to be reversed
         """,
)
st_mask_char = "*"
st_number_of_chars = 15
st_encrypt_key = "WmZq4t7w!z%C&F)J"
st_openai_key = ""
st_openai_model = "text-davinci-003"
if st_operator == "mask":
    st_number_of_chars = st.sidebar.number_input(
        "number of chars", value=st_number_of_chars, min_value=0, max_value=100
    )
    st_mask_char = st.sidebar.text_input(
        "Mask character", value=st_mask_char, max_chars=1
    )
elif st_operator == "encrypt":
    st_encrypt_key = st.sidebar.text_input("AES key", value=st_encrypt_key)
elif st_operator == "synthesize":
    st_openai_key = st.sidebar.text_input(
        "OPENAI_KEY",
        value=os.getenv("OPENAI_KEY", default=""),
        help="See https://help.openai.com/en/articles/4936850-where-do-i-find-my-secret-api-key for more info.",
        type="password",
    )
    st_openai_model = st.sidebar.text_input(
        "OpenAI model for text synthesis",
        value=st_openai_model,
        help="See more here: https://platform.openai.com/docs/models/",
    )
st_threshold = st.sidebar.slider(
    label="Acceptance threshold",
    min_value=0.0,
    max_value=1.0,
    value=0.35,
    help="Define the threshold for accepting a detection as PII. See more here: ",
)

st_return_decision_process = st.sidebar.checkbox(
    "Add analysis explanations to findings",
    value=False,
    help="Add the decision process to the output table. "
         "More information can be found here: https://microsoft.github.io/presidio/analyzer/decision_process/",
)

st_entities = st.sidebar.multiselect(
    label="Which entities to look for?",
    options=get_supported_entities(st_model),
    default=list(get_supported_entities(st_model)),
    help="Limit the list of PII entities detected. "
         "This list is dynamic and based on the NER model and registered recognizers. "
         "More information can be found here: https://microsoft.github.io/presidio/analyzer/adding_recognizers/",
)

# Main panel
analyzer_load_state = st.info("Starting Presidio analyzer...")
engine = analyzer_engine(model_path=st_model)
analyzer_load_state.empty()

# Read default text
with open("demo_text.txt") as f:
    demo_text = f.readlines()

# Create two columns for before and after
col1, col2 = st.columns(2)

# Before:
col1.subheader("Input string:")
st_text = col1.text_area(
    label="Enter text",
    value="".join(demo_text),
    height=400,
)

st_analyze_results = analyze(
    st_model=st_model,
    text=st_text,
    entities=st_entities,
    language="en",
    score_threshold=st_threshold,
    return_decision_process=st_return_decision_process,
)

# After
if st_operator not in ("highlight", "synthesize"):
    with col2:
        st.subheader(f"Output")
        st_anonymize_results = anonymize(
            text=st_text,
            operator=st_operator,
            mask_char=st_mask_char,
            number_of_chars=st_number_of_chars,
            encrypt_key=st_encrypt_key,
            analyze_results=st_analyze_results,
        )
        st.text_area(label="De-identified", value=st_anonymize_results.text, height=400)
elif st_operator == "synthesize":
    with col2:
        st.subheader(f"OpenAI Generated output")
        fake_data = create_fake_data(
            st_text,
            st_analyze_results,
            openai_key=st_openai_key,
            openai_model_name=st_openai_model,
        )
        st.text_area(label="Synthetic data", value=fake_data, height=400)
else:
    st.subheader("Highlighted")
    annotated_tokens = annotate(
        text=st_text,
        analyze_results=st_analyze_results
    )
    # annotated_tokens
    annotated_text(*annotated_tokens)


# json result
class ToDictEncoder(JSONEncoder):
    """Encode dict to json."""

    def default(self, o):
        """Encode to JSON using to_dict."""
        return o.to_dict()


# table result
st.subheader(
    "Findings" if not st_return_decision_process else "Findings with decision factors"
)
if st_analyze_results:
    df = pd.DataFrame.from_records([r.to_dict() for r in st_analyze_results])
    df["text"] = [st_text[res.start: res.end] for res in st_analyze_results]

    df_subset = df[["entity_type", "text", "start", "end", "score"]].rename(
        {
            "entity_type": "Entity type",
            "text": "Text",
            "start": "Start",
            "end": "End",
            "score": "Confidence",
        },
        axis=1,
    )
    df_subset["Text"] = [st_text[res.start: res.end] for res in st_analyze_results]
    if st_return_decision_process:
        analysis_explanation_df = pd.DataFrame.from_records(
            [r.analysis_explanation.to_dict() for r in st_analyze_results]
        )
        df_subset = pd.concat([df_subset, analysis_explanation_df], axis=1)
    st.dataframe(df_subset.reset_index(drop=True), use_container_width=True)
else:
    st.text("No findings")
