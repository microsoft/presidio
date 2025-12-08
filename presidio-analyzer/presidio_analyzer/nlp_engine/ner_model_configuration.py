import logging
from typing import Collection, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

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


class NerModelConfiguration(BaseModel):
    """NER model configuration using Pydantic validation.

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
    """  # noqa: E501

    labels_to_ignore: Optional[Collection[str]] = Field(
        default_factory=list, description="List of labels to ignore"
    )
    aggregation_strategy: Optional[str] = Field(
        default="max", description="Token classification aggregation strategy"
    )
    stride: Optional[int] = Field(
        default=14, description="Stride for token classification"
    )
    alignment_mode: Optional[str] = Field(
        default="expand", description="Alignment mode for spaCy char spans"
    )
    default_score: Optional[float] = Field(
        default=0.85, ge=0.0, le=1.0, description="Default confidence score"
    )
    model_to_presidio_entity_mapping: Optional[Dict[str, str]] = Field(
        default_factory=lambda: MODEL_TO_PRESIDIO_ENTITY_MAPPING.copy(),
        description="Mapping between model entities and Presidio entities",
    )
    low_score_entity_names: Optional[Collection[str]] = Field(
        default_factory=lambda: LOW_SCORE_ENTITY_NAMES.copy(),
        description="Entity names with likely low detection accuracy",
    )
    low_confidence_score_multiplier: Optional[float] = Field(
        default=0.4, ge=0.0, description="Score multiplier for low confidence entities"
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("aggregation_strategy")
    @classmethod
    def validate_aggregation_strategy(cls, agg_strategy: str) -> str:
        """Validate aggregation strategy."""
        valid_strategies = ["simple", "first", "average", "max"]
        if agg_strategy not in valid_strategies:
            logger.warning(
                f"Aggregation strategy '{agg_strategy}' might not be supported. "
                f"Valid options: {valid_strategies}"
            )
        return agg_strategy

    @field_validator("stride")
    @classmethod
    def validate_stride(cls, stride: Optional[int]) -> int:
        """Validate stride and handle None values."""
        if stride is None:
            # Get the default value from the field definition
            return cls.model_fields["stride"].default
        return stride

    @field_validator("alignment_mode")
    @classmethod
    def validate_alignment_mode(cls, alignment: Optional[str]) -> str:
        """Validate alignment mode and handle None values."""
        if alignment is None:
            # Get the default value from the field definition
            return cls.model_fields["alignment_mode"].default
        valid_modes = ["strict", "contract", "expand"]
        if alignment not in valid_modes:
            logger.warning(
                f"Alignment mode '{alignment}' might not be supported. "
                f"Valid options: {valid_modes}"
            )
        return alignment

    @classmethod
    def from_dict(cls, ner_model_configuration_dict: Dict) -> "NerModelConfiguration":
        """
        Create NerModelConfiguration from a dictionary with Pydantic validation.

        :param ner_model_configuration_dict: Dictionary containing configuration
        :return: NerModelConfiguration instance
        """
        return cls(**ner_model_configuration_dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return self.model_dump(exclude_none=True)
