"""Build a Presidio ``AnalyzerEngine`` from declarative YAML configuration.

Each NER option in the demo maps to a committed YAML file under ``config/`` that is
loaded through :class:`~presidio_analyzer.AnalyzerEngineProvider`. Nothing is configured
in Python — the YAML files are the single source of truth. NER for GLiNER and the
OpenMed models is handled by the self-contained ``GLiNERRecognizer`` and
``HuggingFaceNerRecognizer`` declared in those YAML files (i.e. no ``TransformersNlpEngine``);
spaCy and Stanza use their respective NLP engines.

Flair is the only exception: it has no predefined Presidio recognizer class, so its base
YAML is loaded and the sample ``FlairRecognizer`` is attached to the registry afterwards.
"""

import logging
import os
import tempfile

from presidio_analyzer import AnalyzerEngine, AnalyzerEngineProvider

logger = logging.getLogger("presidio-streamlit")

CONFIG_DIR = os.path.join(os.path.dirname(__file__), "config")

# Map a known model selection to its committed YAML config file. spaCy/Stanza/Flair
# are keyed by family; GLiNER and HuggingFace (OpenMed) are keyed by model path so
# several models can share a family.
_CONFIG_FILES = {
    "spacy": "spacy.yaml",
    "stanza": "stanza.yaml",
    "flair": "flair.yaml",
    "nvidia/gliner-PII": "gliner.yaml",
    "knowledgator/gliner-pii-edge-v1.0": "gliner_edge.yaml",
    "OpenMed/OpenMed-PII-GTEMed-Base-149M-v1": "openmed_small.yaml",
    "OpenMed/OpenMed-PII-SuperClinical-Large-434M-v1": "openmed_large.yaml",
}


def config_path_for(model_family: str, model_path: str) -> str:
    """Return the committed YAML config path for a supported model selection."""
    family = model_family.lower()
    if family in ("spacy", "stanza", "flair"):
        filename = _CONFIG_FILES[family]
    elif model_path in _CONFIG_FILES:
        filename = _CONFIG_FILES[model_path]
    else:
        raise ValueError(
            f"No YAML configuration for model '{model_family}/{model_path}'. "
            f"Supported configs: {sorted(_CONFIG_FILES)}"
        )
    return os.path.join(CONFIG_DIR, filename)


def _write_temp_config(config_yaml: str) -> str:
    """Persist user-supplied YAML to a temp file (AnalyzerEngineProvider reads a path)."""
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False, prefix="presidio_demo_cfg_"
    )
    tmp.write(config_yaml)
    tmp.close()
    return tmp.name


def create_analyzer_engine(
    model_family: str, model_path: str, config_yaml: str = None
) -> AnalyzerEngine:
    """Create an ``AnalyzerEngine`` for the requested NER model from YAML config.

    :param model_family: NER package — one of spacy, stanza, gliner, flair, huggingface.
    :param model_path: Model name/path (e.g. ``en_core_web_lg``,
        ``urchade/gliner_multi_pii-v1``, ``OpenMed/OpenMed-PII-...``).
    :param config_yaml: Optional raw YAML to build from instead of the committed
        config file (used by the in-app editor when ``ALLOW_CONFIG_EDIT`` is set).
    """
    if config_yaml is not None:
        conf_file = _write_temp_config(config_yaml)
    else:
        conf_file = config_path_for(model_family, model_path)
    logger.info(f"Loading analyzer config for {model_family}/{model_path}: {conf_file}")

    # FlairRecognizer is a custom (sample) recognizer, not a Presidio built-in.
    # Importing the module registers it as an EntityRecognizer subclass, which is
    # how Presidio's YAML loader discovers it by class name — so it can be declared
    # directly in flair.yaml (type: predefined) instead of added in code.
    if model_family.lower() == "flair":
        import flair_recognizer  # noqa: F401

    return AnalyzerEngineProvider(
        analyzer_engine_conf_file=conf_file
    ).create_engine()
