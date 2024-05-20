"""Install the default NLP models defined in the provided yaml file."""

import argparse
import logging
from typing import Dict, Union

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


def install_models(conf_file: str) -> None:
    """Installs models in conf/default.yaml.

    :param conf_file: Path to the yaml file containing the models to install.
    See examples in the conf directory.
    """

    nlp_configuration = yaml.safe_load(open(conf_file))

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
    args = parser.parse_args()

    install_models(conf_file=args.conf_file)
