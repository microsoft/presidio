"""Install the default NLP models defined in the provided yaml file."""

import logging
import argparse
import spacy
import yaml

try:
    import stanza
except ImportError:
    # stanza should be installed manually
    stanza = None

logger = logging.getLogger()
logger.setLevel("INFO")
logger.addHandler(logging.StreamHandler())


def install_models(conf_file: str) -> None:
    """Installs models in conf/default.yaml."""
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


def _download_model(engine_name: str, model_name: str) -> None:
    if engine_name not in ("spacy", "stanza"):
        raise ValueError(f"Unsupported nlp engine: {engine_name}")

    if engine_name == "spacy":
        spacy.cli.download(model_name)
    elif engine_name == "stanza":
        if stanza:
            stanza.download(model_name)
        else:
            raise ImportError("stanza is not installed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Install NLP models into the presidio-analyzer Docker container"
    )
    parser.add_argument(
        "--conf_file",
        required=False,
        default="conf/default.yaml",
        help="Location of nlp configuration yaml file. Default: conf/default.yaml",
    )
    args = parser.parse_args()

    install_models(conf_file=args.conf_file)
