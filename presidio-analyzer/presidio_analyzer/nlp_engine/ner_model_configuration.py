import logging
from dataclasses import dataclass
from typing import Collection, Dict, Optional, Type

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

LOW_SCORE_ENTITY_NAMES = set()
LABELS_TO_IGNORE = {
    "O",
    "ORG",
    "ORGANIZATION",
    "CARDINAL",
    "EVENT",
    "LANGUAGE",
    "LAW",
    "MONEY",
    "ORDINAL",
    "PERCENT",
    "PRODUCT",
    "QUANTITY",
    "WORK_OF_ART",
}


@dataclass
class NerModelConfiguration:
    """NER model configuration.

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

    labels_to_ignore: Optional[Collection[str]] = None
    aggregation_strategy: Optional[str] = "max"
    stride: Optional[int] = 14
    alignment_mode: Optional[str] = "expand"
    default_score: Optional[float] = 0.85
    model_to_presidio_entity_mapping: Optional[Dict[str, str]] = None
    low_score_entity_names: Optional[Collection] = None
    low_confidence_score_multiplier: Optional[float] = 0.4

    def __post_init__(self):
        """Validate the configuration and set defaults."""
        if self.model_to_presidio_entity_mapping is None:
            logger.warning(
                "model_to_presidio_entity_mapping is missing from configuration, "
                "using default"
            )
            self.model_to_presidio_entity_mapping = MODEL_TO_PRESIDIO_ENTITY_MAPPING
        if self.low_score_entity_names is None:
            logger.warning(
                "low_score_entity_names is missing from configuration, " "using default"
            )
            self.low_score_entity_names = LOW_SCORE_ENTITY_NAMES
        if self.labels_to_ignore is None:
            logger.warning(
                "labels_to_ignore is missing from configuration, " "using default"
            )
            self.labels_to_ignore = LABELS_TO_IGNORE

    @classmethod
    def _validate_input(cls, ner_model_configuration_dict: Dict) -> None:
        key_to_type = {
            "labels_to_ignore": Collection,
            "aggregation_strategy": str,
            "alignment_mode": str,
            "model_to_presidio_entity_mapping": dict,
            "low_confidence_score_multiplier": float,
            "low_score_entity_names": Collection,
            "stride": int,
        }

        for key, field_type in key_to_type.items():
            cls.__validate_type(
                config_dict=ner_model_configuration_dict, key=key, field_type=field_type
            )

    @staticmethod
    def __validate_type(config_dict: Dict, key: str, field_type: Type) -> None:
        if key in config_dict:
            if not isinstance(config_dict[key], field_type):
                raise ValueError(f"{key} must be of type {field_type}")

    @classmethod
    def from_dict(cls, nlp_engine_configuration: Dict) -> "NerModelConfiguration":
        """Load NLP engine configuration from dict.

        :param nlp_engine_configuration: Dict with the configuration to load.
        """
        cls._validate_input(nlp_engine_configuration)

        return cls(**nlp_engine_configuration)

    def to_dict(self) -> Dict:
        """Return the configuration as a dict."""
        return self.__dict__

    def __str__(self) -> str:  # noqa D105
        return str(self.to_dict())

    def __repr__(self) -> str:  # noqa D105
        return str(self)
