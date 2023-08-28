import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Union, Collection

import yaml

logger = logging.getLogger("presidio-analyzer")

MODEL_TO_PRESIDIO_ENTITY_MAPPING = dict(
    PER="PERSON",
    PERSON="PERSON",
    LOC="LOCATION",
    LOCATION="LOCATION",
    GPE="LOCATION",
    ORG="ORGANIZATION",
    DATE="DATE_TIME",
    TIME="DATE_TIME",
    NORP="NRP",
    AGE="AGE",
    ID="ID",
    EMAIL="EMAIL",
    PATIENT="PERSON",
    STAFF="PERSON",
    HOSP="ORGANIZATION",
    PATORG="ORGANIZATION",
    PHONE="PHONE_NUMBER",
    HCW="PERSON",
    HOSPITAL="ORGANIZATION",
)

LOW_SCORE_ENTITY_NAMES = {"ORG", "ORGANIZATION"}
LABELS_TO_IGNORE = {"O"}


@dataclass
class NerModelConfiguration:
    """NER model configuration.

    :param nlp_engine_name: Name of the NLP engine to use.
    :param labels_to_ignore: List of labels to not return predictions for.
    :param aggregation_strategy:
    See https://huggingface.co/docs/transformers/main_classes/pipelines#transformers.TokenClassificationPipeline.aggregation_strategy
    :param stride:
    See https://huggingface.co/docs/transformers/main_classes/pipelines#transformers.TokenClassificationPipeline.stride
    :param alignment_mode: See https://spacy.io/api/doc#char_span
    :param default_score: Default confidence score if the model does not provide one.
    :param model_to_presidio_entity_mapping:
    Mapping between the NER model entities and Presidio entities.
    :param low_score_entity_names:
    Set of entity names that are likely to have low detection accuracy that should be adjusted.
    :param low_confidence_score_multiplier: A multiplier for the score given for low_score_entity_names.
    Multiplier to the score given for low_score_entity_names.
    """  # noqa E501

    nlp_engine_name: str
    labels_to_ignore: Optional[Collection[str]] = None
    aggregation_strategy: Optional[str] = "simple"
    stride: Optional[int] = 14
    alignment_mode: Optional[str] = "strict"
    default_score: Optional[float] = 0.85
    model_to_presidio_entity_mapping: Optional[Dict[str, str]] = None
    low_score_entity_names: Optional[Collection] = None
    low_confidence_score_multiplier: Optional[float] = 0.4

    def __post_init__(self):
        if self.model_to_presidio_entity_mapping is None:
            self.model_to_presidio_entity_mapping = MODEL_TO_PRESIDIO_ENTITY_MAPPING
        if self.low_score_entity_names is None:
            self.low_score_entity_names = LOW_SCORE_ENTITY_NAMES
        if self.labels_to_ignore is None:
            self.labels_to_ignore = LABELS_TO_IGNORE

    @classmethod
    def _validate_input(cls, nlp_engine_configuration: Dict):
        if "nlp_engine_name" not in nlp_engine_configuration:
            raise ValueError("nlp_engine_name is a required parameter")
        if "labels_to_ignore" in nlp_engine_configuration:
            if not isinstance(nlp_engine_configuration["labels_to_ignore"], list):
                raise ValueError("labels_to_ignore must be a list")
        if "aggregation_strategy" in nlp_engine_configuration:
            if not isinstance(nlp_engine_configuration["aggregation_strategy"], str):
                raise ValueError("aggregation_strategy must be a string")
        if "alignment_mode" in nlp_engine_configuration:
            if not isinstance(nlp_engine_configuration["alignment_mode"], str):
                raise ValueError("alignment_mode must be a string")
        if "stride" in nlp_engine_configuration:
            if not isinstance(nlp_engine_configuration["stride"], int):
                raise ValueError("stride must be an integer")
        if "model_to_presidio_entity_mapping" in nlp_engine_configuration:
            if not isinstance(
                nlp_engine_configuration["model_to_presidio_entity_mapping"], dict
            ):
                raise ValueError("model_to_presidio_entity_mapping must be a dict")
        if "low_score_entity_names" in nlp_engine_configuration:
            if not isinstance(nlp_engine_configuration["low_score_entity_names"], list):
                raise ValueError("low_score_entity_names must be a list")
        if "low_confidence_score_multiplier" in nlp_engine_configuration:
            if not isinstance(
                nlp_engine_configuration["low_confidence_score_multiplier"], float
            ):
                raise ValueError("low_confidence_score_multiplier must be a float")

    @classmethod
    def from_yaml(cls, yaml_file: Union[Path, str]) -> "NerModelConfiguration":
        """Load NLP engine configuration from yaml file.

        :param yaml_file: Path to the yaml file."""

        if not Path(yaml_file).exists():
            raise FileNotFoundError(f"configuration file {yaml_file} not found.")

        with open(yaml_file, "r") as f:
            nlp_engine_configuration = yaml.safe_load(f)

        cls._validate_input(nlp_engine_configuration)

        return cls.from_dict(nlp_engine_configuration)

    @classmethod
    def from_json(cls, json_file: Union[Path, str]) -> "NerModelConfiguration":
        """Load NLP engine configuration from json file.

        :param json_file: Path to the json file."""

        if not Path(json_file).exists():
            raise FileNotFoundError(f"configuration file {json_file} not found.")

        with open(json_file, "r") as f:
            nlp_engine_configuration = json.load(f)

        cls._validate_input(nlp_engine_configuration)

        return cls.from_dict(nlp_engine_configuration)

    @classmethod
    def from_dict(cls, config_dict: Dict) -> "NerModelConfiguration":
        """Load NLP engine configuration from dict.

        :param config_dict: Dict with the configuration to load.
        """
        return cls(**config_dict)

    def to_dict(self) -> Dict:
        """Return the configuration as a dict."""
        return self.__dict__

    @staticmethod
    def get_full_conf_path(
        default_conf_file: Union[Path, str] = "default.yaml"
    ) -> Path:
        """Return a Path to the default conf file.

        :param default_conf_file: Name of the default conf file."""
        return Path(Path(__file__).parent.parent.parent, "conf", default_conf_file)

    def __str__(self) -> str:
        return str(self.to_dict())

    def __repr__(self) -> str:
        return str(self)
