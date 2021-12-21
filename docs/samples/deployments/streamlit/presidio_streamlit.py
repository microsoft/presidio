"""Streamlit app for Presidio."""

import json
from json import JSONEncoder

import pandas as pd
import streamlit as st
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine


# Helper methods
@st.cache(allow_output_mutation=True)
def analyzer_engine():
    return AnalyzerEngine()


@st.cache(allow_output_mutation=True)
def anonymizer_engine():
    return AnonymizerEngine()


def get_supported_entities():
    return analyzer_engine().get_supported_entities()


def get_supported_anonymizers():
    return anonymizer_engine().get_anonymizers()


def analyze(text, entities, analyzer_engine, score_threshold):
    if "All" in entities:
        entities = None
    return analyzer_engine.analyze(
        text=text,
        language="en",
        entities=entities,
        score_threshold=score_threshold,
        return_decision_process=True,
    )


def anonymize(text, analyze_results):

    res = anonymizer_engine().anonymize(text, analyze_results)
    return res.text


st.set_page_config(page_title="Presidio demo", layout="wide")

# Side bar
st.sidebar.markdown(
    """
Anonymize PII entities with [presidio](https://aka.ms/presidio).
"""
)

st_entities = st.sidebar.multiselect(
    label="Which entities to look for?",
    options=get_supported_entities(),
    default=list(get_supported_entities()),
)

st_threhsold = st.sidebar.slider(
    label="Acceptance threshold", min_value=0.0, max_value=1.0, value=0.35
)

st.sidebar.info(
    "Presidio is an open source framework for PII detection and anonymization. "
    "For more info visit [aka.ms/presidio](https://aka.ms/presidio)"
)

# Main panel
analyzer_load_state = st.info(f"Starting Presidio analyzer...")
engine = analyzer_engine()
analyzer_load_state.empty()


# Create two columns for before and after
col1, col2 = st.beta_columns(2)

# Before:
col1.subheader("Input string:")
st_text = col1.text_area(
    label="Enter text",
    value="Type in some text, "
    "like a phone number (212-141-4544) "
    "or a name (Lebron James).",
    height=400,
)

# After
col2.subheader("Output:")

st_analyze_results = analyze(
    text=st_text,
    entities=st_entities,
    analyzer_engine=engine,
    score_threshold=st_threhsold,
)
st_anonymize_results = anonymize(st_text, st_analyze_results)
col2.text_area(label="", value=st_anonymize_results, height=400)


# table result
st.subheader("Findings")
df = pd.DataFrame.from_records([r.to_dict() for r in st_analyze_results])
df = df[["entity_type", "start", "end", "score"]].rename(
    {
        "entity_type": "Entity type",
        "start": "Start",
        "end": "End",
        "score": "Confidence",
    },
    axis=1,
)


st.dataframe(df, width=1000)


# json result
class ToDictEncoder(JSONEncoder):
    def default(self, o):
        return o.to_dict()


if st.button("Show analyzer results json"):
    st.json(json.dumps(st_analyze_results, cls=ToDictEncoder))