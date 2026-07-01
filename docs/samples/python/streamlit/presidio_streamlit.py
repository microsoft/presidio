"""Streamlit app for Presidio."""

import logging
import os
import re
import traceback

import dotenv
import pandas as pd
import streamlit as st
from annotated_text import annotated_text
from openai_fake_data_generator import OpenAIParams
from presidio_analyzer_config import config_path_for
from presidio_branding import apply_branding
from presidio_helpers import (
    analyze,
    analyzer_engine,
    annotate,
    anonymize,
    create_fake_data,
    get_supported_entities,
)

st.set_page_config(
    page_title="Presidio demo",
    page_icon="🐙",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "https://data-privacy-stack.github.io/presidio/",
    },
)

# Apply the Data Privacy Stack brand (colors, fonts, octopus logo).
apply_branding()

dotenv.load_dotenv()
logger = logging.getLogger("presidio-streamlit")


def parse_word_list(raw: str) -> list:
    """Split a free-text allow/deny list (newline- or comma-separated) into words."""
    return [word.strip() for word in re.split(r"[,\n]", raw or "") if word.strip()]


# Sidebar
st.sidebar.header(
    """
PII De-Identification with [Presidio](https://data-privacy-stack.github.io/presidio/)
"""
)


model_help_text = """
    Select which Named Entity Recognition (NER) model to use for PII detection, in parallel to rule-based recognizers.
    Presidio supports multiple NER packages off-the-shelf, such as spaCy, GLiNER, OpenMed (via HuggingFace), Stanza and Flair.
    """

model_list = [
    "spaCy/en_core_web_lg",
    "GLiNER/nvidia/gliner-PII",
    "GLiNER/knowledgator/gliner-pii-edge-v1.0",
    "HuggingFace/OpenMed/OpenMed-PII-GTEMed-Base-149M-v1",
    "HuggingFace/OpenMed/OpenMed-PII-SuperClinical-Large-434M-v1",
    "flair/ner-english-large",
    "stanza/en",
]
# Select model
st_model = st.sidebar.selectbox(
    "NER model package",
    model_list,
    index=1,
    help=model_help_text,
)

# Extract model package.
st_model_package = st_model.split("/")[0]

# Remove package prefix (if needed)
st_model = (
    st_model
    if st_model_package.lower() not in ("spacy", "stanza", "huggingface", "gliner")
    else "/".join(st_model.split("/")[1:])
)

st.sidebar.warning("Note: Models might take some time to download. ")

st.sidebar.caption(
    "This demo only supports English, but Presidio can be configured to support "
    "[multiple languages](https://data-privacy-stack.github.io/presidio/analyzer/languages/)."
)

analyzer_params = (st_model_package, st_model)
logger.debug(f"analyzer_params: {analyzer_params}")

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

open_ai_params = None

logger.debug(f"st_operator: {st_operator}")


def set_up_openai_synthesis():
    """Set up the OpenAI API key and model for text synthesis."""

    if os.getenv("OPENAI_TYPE", default="openai") == "Azure":
        openai_api_type = "azure"
        st_openai_api_base = st.sidebar.text_input(
            "Azure OpenAI base URL",
            value=os.getenv("AZURE_OPENAI_ENDPOINT", default=""),
        )
        openai_key = os.getenv("AZURE_OPENAI_KEY", default="")
        st_deployment_id = st.sidebar.text_input(
            "Deployment name", value=os.getenv("AZURE_OPENAI_DEPLOYMENT", default="")
        )
        st_openai_version = st.sidebar.text_input(
            "OpenAI version",
            value=os.getenv("OPENAI_API_VERSION", default="2023-05-15"),
        )
    else:
        openai_api_type = "openai"
        st_openai_version = st_openai_api_base = None
        st_deployment_id = ""
        openai_key = os.getenv("OPENAI_API_KEY", default=os.getenv("OPENAI_KEY", ""))
    st_openai_key = st.sidebar.text_input(
        "OpenAI API key",
        value=openai_key,
        help="See https://help.openai.com/en/articles/4936850-where-do-i-find-my-secret-api-key for more info.",
        type="password",
    )
    st_openai_model = st.sidebar.text_input(
        "OpenAI model for text synthesis",
        value=os.getenv("OPENAI_MODEL", default="gpt-4o-mini"),
        help="See more here: https://platform.openai.com/docs/models/",
    )
    return (
        openai_api_type,
        st_openai_api_base,
        st_deployment_id,
        st_openai_version,
        st_openai_key,
        st_openai_model,
    )


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
    (
        openai_api_type,
        st_openai_api_base,
        st_deployment_id,
        st_openai_version,
        st_openai_key,
        st_openai_model,
    ) = set_up_openai_synthesis()

    open_ai_params = OpenAIParams(
        openai_key=st_openai_key,
        model=st_openai_model,
        api_base=st_openai_api_base,
        deployment_id=st_deployment_id,
        api_version=st_openai_version,
        api_type=openai_api_type,
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
    "More information can be found here: https://data-privacy-stack.github.io/presidio/analyzer/decision_process/",
)

# Allow and deny lists
st_deny_allow_expander = st.sidebar.expander(
    "Allowlists and denylists",
    expanded=False,
)

with st_deny_allow_expander:
    st_allow_list = parse_word_list(
        st.text_area(
            label="Add words to the allowlist",
            help="One word per line (or comma-separated).",
            key="allow_list",
        )
    )
    st.caption(
        "Allowlists contain words that are not considered PII, but are detected as such."
    )

    st_deny_list = parse_word_list(
        st.text_area(
            label="Add words to the denylist",
            help="One word per line (or comma-separated).",
            key="deny_list",
        )
    )
    st.caption(
        "Denylists contain words that are considered PII, but are not detected as such."
    )
# Main panel

with st.expander("About this demo", expanded=False):
    st.info(
        """Presidio is an open source customizable framework for PII detection and de-identification,
        an independent, community-governed project under the Data Privacy Stack organization.
        \n\n[Code](https://github.com/data-privacy-stack/presidio) |
        [Tutorial](https://data-privacy-stack.github.io/presidio/tutorial/) | 
        [Installation](https://data-privacy-stack.github.io/presidio/installation/) | 
        [FAQ](https://data-privacy-stack.github.io/presidio/faq/)
        """
    )

    st.info(
        """
    Use this demo to:
    - Experiment with different off-the-shelf models and NLP packages.
    - Explore the different de-identification options, including redaction, masking, encryption and more.
    - Generate synthetic text with Presidio and OpenAI.
    - Configure allow and deny lists.
    
    This demo website shows some of Presidio's capabilities.
    [Visit our website](https://data-privacy-stack.github.io/presidio) for more info,
    samples and deployment options.    
    """
    )

    st.markdown(
        "[![Pypi Downloads](https://img.shields.io/pypi/dm/presidio-analyzer.svg)](https://img.shields.io/pypi/dm/presidio-analyzer.svg)"
        "[![MIT license](https://img.shields.io/badge/license-MIT-brightgreen.svg)](https://opensource.org/licenses/MIT)"
        "![GitHub Repo stars](https://img.shields.io/github/stars/data-privacy-stack/presidio?style=social)"
    )

# Model configuration (YAML) — read-only by default; editable when ALLOW_CONFIG_EDIT is set.
# The value is resolved here (from session state); the viewer/editor itself is rendered
# lower, between the text panels and the findings table (see ``config_container``).
allow_config_edit = os.getenv("ALLOW_CONFIG_EDIT", "").lower() in ("1", "true", "yes")
st_config_yaml = None
config_text = None
config_path = None
config_editor_key = f"config_yaml_editor::{st_model_package}/{st_model}"
try:
    config_path = config_path_for(st_model_package, st_model)
    with open(config_path) as config_file:
        config_text = config_file.read()
    # If the user has edited this model's YAML in the editor below, build from it.
    if allow_config_edit:
        current_yaml = st.session_state.get(config_editor_key, config_text)
        if current_yaml.strip() != config_text.strip():
            st_config_yaml = current_yaml
except Exception as config_err:
    logger.warning(f"Could not load YAML config: {config_err}")

analyzer_load_state = st.info("Starting Presidio analyzer...")

analyzer_load_state.empty()

# Read default text
with open("demo_text.txt") as f:
    demo_text = f.readlines()

# Create two columns for before and after
col1, col2 = st.columns(2)

# Before:
col1.subheader("Input")
st_text = col1.text_area(
    label="Enter text", value="".join(demo_text), height=400, key="text_input"
)

# Reserved slot for the model-configuration YAML, shown between the text panels
# above and the findings table below. Filled after analysis so it always renders
# (even if an invalid edit makes analysis error, the editor stays available to fix).
config_container = st.container()

try:
    # Choose entities
    st_entities_expander = st.sidebar.expander("Choose entities to look for")
    st_entities = st_entities_expander.multiselect(
        label="Which entities to look for?",
        options=get_supported_entities(*analyzer_params, config_yaml=st_config_yaml),
        default=list(
            get_supported_entities(*analyzer_params, config_yaml=st_config_yaml)
        ),
        help="Limit the list of PII entities detected. "
        "This list is dynamic and based on the NER model and registered recognizers. "
        "More information can be found here: https://data-privacy-stack.github.io/presidio/analyzer/adding_recognizers/",
    )

    # Before
    analyzer_load_state = st.info("Starting Presidio analyzer...")
    analyzer = analyzer_engine(*analyzer_params, config_yaml=st_config_yaml)
    analyzer_load_state.empty()

    st_analyze_results = analyze(
        *analyzer_params,
        config_yaml=st_config_yaml,
        text=st_text,
        entities=st_entities,
        language="en",
        score_threshold=st_threshold,
        return_decision_process=st_return_decision_process,
        allow_list=st_allow_list,
        deny_list=st_deny_list,
    )

    # After
    if st_operator not in ("highlight", "synthesize"):
        with col2:
            st.subheader("Output")
            st_anonymize_results = anonymize(
                text=st_text,
                operator=st_operator,
                mask_char=st_mask_char,
                number_of_chars=st_number_of_chars,
                encrypt_key=st_encrypt_key,
                analyze_results=st_analyze_results,
            )
            st.text_area(
                label="De-identified", value=st_anonymize_results.text, height=400
            )
    elif st_operator == "synthesize":
        with col2:
            st.subheader("OpenAI Generated output")
            fake_data = create_fake_data(
                st_text,
                st_analyze_results,
                open_ai_params,
            )
            st.text_area(label="Synthetic data", value=fake_data, height=400)
    else:
        st.subheader("Highlighted")
        annotated_tokens = annotate(text=st_text, analyze_results=st_analyze_results)
        # annotated_tokens
        annotated_text(*annotated_tokens)

    # table result
    st.subheader(
        "Findings"
        if not st_return_decision_process
        else "Findings with decision factors"
    )
    if st_analyze_results:
        df = pd.DataFrame.from_records([r.to_dict() for r in st_analyze_results])
        df["text"] = [st_text[res.start : res.end] for res in st_analyze_results]

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
        df_subset["Text"] = [st_text[res.start : res.end] for res in st_analyze_results]
        if st_return_decision_process:
            analysis_explanation_df = pd.DataFrame.from_records(
                [r.analysis_explanation.to_dict() for r in st_analyze_results]
            )
            df_subset = pd.concat([df_subset, analysis_explanation_df], axis=1)
        st.dataframe(df_subset.reset_index(drop=True), width="stretch")
    else:
        st.text("No findings")

except Exception as e:
    print(e)
    traceback.print_exc()
    st.error(e)

# Render the model-configuration YAML into the slot reserved above (between the
# text panels and the findings table).
with config_container:
    if config_text is not None and config_path is not None:
        with st.expander("Model configuration (YAML)", expanded=False):
            st.caption(
                "This NER setup is loaded declaratively via Presidio's "
                f"`AnalyzerEngineProvider` from `config/{os.path.basename(config_path)}`."
            )
            if allow_config_edit:
                st.text_area(
                    "Edit the configuration — the analyzer rebuilds from this YAML:",
                    value=config_text,
                    height=400,
                    key=config_editor_key,
                )
            else:
                st.code(config_text, language="yaml")
                st.caption(
                    "Set `ALLOW_CONFIG_EDIT=true` to edit this configuration in-app."
                )

# Microsoft Clarity telemetry (kept intentionally). st.html with
# unsafe_allow_javascript runs the script in the app document — the
# non-deprecated replacement for streamlit.components.v1.html.
st.html(
    """
    <script type="text/javascript">
    (function(c,l,a,r,i,t,y){
        c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
        t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
        y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
    })(window, document, "clarity", "script", "h7f8bp42n8");
    </script>
    """,
    unsafe_allow_javascript=True,
)
