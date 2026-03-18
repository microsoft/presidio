"""Install the default NLP models defined in the provided yaml file."""

import argparse
import logging
from typing import Dict, Optional, Union

import yaml
from spacy.cli import download as spacy_download

try:
    import stanza
except ImportError:
    # stanza should be installed manually
    stanza = None

try:
    import transformers
    from huggingface_hub import snapshot_download
    from transformers import AutoModelForTokenClassification, AutoTokenizer
except ImportError:
    # transformers should be installed manually
    transformers = None

logger = logging.getLogger()
logger.setLevel("INFO")
logger.addHandler(logging.StreamHandler())


def install_models(
    conf_file: str, analyzer_conf_file: Optional[str] = None
) -> None:
    """Installs NLP models based on the provided configuration files.

    When *analyzer_conf_file* is given and contains an ``nlp_configuration``
    section (unified analyzer conf format), the models defined there are
    downloaded and *conf_file* is ignored.  This ensures that a single unified
    ``ANALYZER_CONF_FILE`` can drive both build-time model downloads and
    runtime configuration without requiring a separate ``NLP_CONF_FILE``.

    When *analyzer_conf_file* is not provided or does not contain an
    ``nlp_configuration`` section, *conf_file* is used as before (plain NLP
    conf format with a top-level ``nlp_engine_name`` and ``models`` field).

    :param conf_file: Path to a plain NLP configuration yaml file.
    :param analyzer_conf_file: Optional path to a unified analyzer conf file
        that may contain an ``nlp_configuration`` section.
    """
    # Prefer nlp_configuration embedded inside a unified ANALYZER_CONF_FILE.
    if analyzer_conf_file:
        try:
            with open(analyzer_conf_file) as fh:
                analyzer_config = yaml.safe_load(fh)
        except OSError as e:
            raise OSError(
                f"Could not read analyzer conf file '{analyzer_conf_file}'"
            ) from e
        if analyzer_config and "nlp_configuration" in analyzer_config:
            logger.info(
                "Using nlp_configuration from analyzer conf file: %s",
                analyzer_conf_file,
            )
            _install_models_from_nlp_config(analyzer_config["nlp_configuration"])
            return

    # Fall back to the plain NLP conf file (backward-compatible path).
    try:
        with open(conf_file) as fh:
            nlp_configuration = yaml.safe_load(fh)
    except OSError as e:
        raise OSError(f"Could not read NLP conf file '{conf_file}'") from e
    _install_models_from_nlp_config(nlp_configuration)


def _install_models_from_nlp_config(nlp_configuration: dict) -> None:
    """Download all models described in an nlp_configuration dict.

    :param nlp_configuration: Dict with at least ``nlp_engine_name`` and
        ``models`` keys (i.e. the content of a plain NLP conf file, or the
        value of the ``nlp_configuration`` key in a unified analyzer conf).
    """
    logger.info(f"Installing models from configuration: {nlp_configuration}")

    if "nlp_engine_name" not in nlp_configuration:
        raise ValueError("NLP config file should contain an nlp_engine_name field")

    if "models" not in nlp_configuration:
        raise ValueError("NLP config file should contain a list of models")

    for model in nlp_configuration["models"]:
        engine_name = nlp_configuration["nlp_engine_name"]
        model_name = model["model_name"]
        _download_model(engine_name, model_name)

    logger.info("finished installing models")


def _download_model(engine_name: str, model_name: Union[str, Dict[str, str]]) -> None:
    if engine_name == "spacy":
        spacy_download(model_name)
    elif engine_name == "stanza":
        if stanza:
            stanza.download(model_name)
        else:
            raise ImportError("stanza is not installed")
    elif engine_name == "transformers":
        if transformers:
            _install_transformers_spacy_models(model_name)
        else:
            raise ImportError("transformers is not installed")
    else:
        raise ValueError(f"Unsupported nlp engine: {engine_name}")


def _install_transformers_spacy_models(model_name: Dict[str, str]) -> None:
    if "spacy" not in model_name:
        raise ValueError(
            "transformers config should contain "
            "a spacy model/pipeline such as en_core_web_sm"
        )
    if "transformers" not in model_name:
        raise ValueError(
            "transformers config should contain a path to a transformers model"
        )

    spacy_model = model_name["spacy"]
    transformers_model = model_name["transformers"]

    # download spacy model/pipeline
    logger.info(f"Installing spaCy model: {spacy_model}")
    spacy_download(spacy_model)

    # download transformers model
    logger.info(f"Installing transformers model: {transformers_model}")
    snapshot_download(repo_id=transformers_model)

    # Instantiate to make sure it's downloaded during installation and not runtime
    AutoTokenizer.from_pretrained(transformers_model)
    AutoModelForTokenClassification.from_pretrained(transformers_model)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Install NLP models into the presidio-analyzer Docker container"
    )
    parser.add_argument(
        "--conf_file",
        required=False,
        default="presidio_analyzer/conf/default.yaml",
        help="Location of nlp configuration yaml file. Default: conf/default.yaml",
    )
    parser.add_argument(
        "--analyzer_conf_file",
        required=False,
        default=None,
        help=(
            "Optional path to a unified analyzer conf file (ANALYZER_CONF_FILE). "
            "When this file contains an nlp_configuration section, models from "
            "that section are downloaded and --conf_file is ignored. "
            "Use this when ANALYZER_CONF_FILE is the single source of truth for "
            "both NLP and recognizer-registry configuration."
        ),
    )
    args = parser.parse_args()

    install_models(
        conf_file=args.conf_file,
        analyzer_conf_file=args.analyzer_conf_file,
    )
