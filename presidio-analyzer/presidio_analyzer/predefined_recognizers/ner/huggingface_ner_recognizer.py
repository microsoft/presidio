"""HuggingFace NER Recognizer for direct NER model inference.

This recognizer uses HuggingFace Transformers pipeline directly,
bypassing spaCy tokenizer alignment issues that commonly occur
with agglutinative languages (Korean, Japanese, Turkish, etc.).

The spaCy tokenizer tends to include particles/postpositions with nouns,
causing alignment_mode issues:
- NER result: "김태웅" (entity only)
- spaCy token: "김태웅이고" (entity + particle)
- char_span alignment fails

This recognizer solves the problem by using the HuggingFace NER model's
own tokenizer and returning results directly without spaCy alignment.
"""

import logging
from typing import Dict, List, Optional

from presidio_analyzer import (
    AnalysisExplanation,
    LocalRecognizer,
    RecognizerResult,
)
from presidio_analyzer.nlp_engine import NlpArtifacts, device_detector

try:
    from transformers import pipeline as hf_pipeline
except ImportError:
    hf_pipeline = None


logger = logging.getLogger("presidio-analyzer")


class HuggingFaceNerRecognizer(LocalRecognizer):
    """HuggingFace Transformers based NER Recognizer.

    This recognizer uses HuggingFace pipeline directly for NER,
    bypassing spaCy tokenizer alignment issues. It's particularly
    useful for agglutinative languages (Korean, Japanese, Turkish, etc.)
    where particles attach to nouns.

    Unlike the standard TransformersNlpEngine approach, this recognizer:
    - Uses HuggingFace pipeline directly (not through spaCy)
    - Returns NER results without char_span alignment
    - Supports any HuggingFace token-classification model
    - Works with any language that has a HuggingFace NER model

    Example:
        >>> from presidio_analyzer import AnalyzerEngine
        >>> from presidio_analyzer.predefined_recognizers.ner import (
        ...     HuggingFaceNerRecognizer
        ... )
        >>>
        >>> # For Korean
        >>> recognizer = HuggingFaceNerRecognizer(
        ...     model_name="Leo97/KoELECTRA-small-v3-modu-ner",
        ...     supported_language="ko"
        ... )
        >>> recognizer.load()
        >>>
        >>> # For English
        >>> recognizer = HuggingFaceNerRecognizer(
        ...     model_name="dslim/bert-base-NER",
        ...     supported_language="en"
        ... )
        >>>
        >>> analyzer = AnalyzerEngine()
        >>> analyzer.registry.add_recognizer(recognizer)
    """

    # Default label mapping from common NER models to Presidio entities
    DEFAULT_LABEL_MAPPING = {
        # Standard NER labels (CoNLL format)
        "PER": "PERSON",
        "LOC": "LOCATION",
        "ORG": "ORGANIZATION",
        "MISC": "MISC",
        # Date/Time labels
        "DAT": "DATE_TIME",
        "DATE": "DATE_TIME",
        "TIME": "DATE_TIME",
        # Korean model labels (KoELECTRA, etc.)
        "PS": "PERSON",
        "LC": "LOCATION",
        "OG": "ORGANIZATION",
        "DT": "DATE_TIME",
        "TI": "DATE_TIME",
        # BERT-base-NER style labels (with B-/I- prefix stripped)
        "PERSON": "PERSON",
        "LOCATION": "LOCATION",
        "ORGANIZATION": "ORGANIZATION",
        "DATE_TIME": "DATE_TIME",
    }

    def __init__(
        self,
        supported_entities: Optional[List[str]] = None,
        name: str = "HuggingFaceNerRecognizer",
        supported_language: str = "en",
        version: str = "0.0.1",
        context: Optional[List[str]] = None,
        model_name: Optional[str] = None,
        label_mapping: Optional[Dict[str, str]] = None,
        threshold: float = 0.3,
        aggregation_strategy: str = "simple",
        map_location: Optional[str] = None,
    ):
        """Initialize the HuggingFace NER Recognizer.

        :param supported_entities: List of supported entities.
            If None, uses entities from label_mapping.
        :param name: Name of the recognizer
        :param supported_language: Language code (e.g., "en", "ko", "ja")
        :param version: Version of the recognizer
        :param context: Context words (N/A for this recognizer)
        :param model_name: HuggingFace model name or path.
            If None, must be set before calling load().
        :param label_mapping: Mapping from model labels to Presidio entities.
            If None, uses DEFAULT_LABEL_MAPPING.
        :param threshold: Minimum confidence score threshold (0.0 - 1.0)
        :param aggregation_strategy: Token aggregation strategy
            ("simple", "first", "average", "max")
        :param map_location: Device to use ("cuda", "cpu", or None for auto)
        """
        self.model_name = model_name
        self.label_mapping = label_mapping or self.DEFAULT_LABEL_MAPPING
        self.threshold = threshold
        self.aggregation_strategy = aggregation_strategy
        self.map_location = (
            map_location if map_location else device_detector.get_device()
        )
        self.ner_pipeline = None

        # Derive supported entities from label mapping
        if supported_entities:
            _supported_entities = supported_entities
        else:
            _supported_entities = list(set(self.label_mapping.values()))

        super().__init__(
            supported_entities=_supported_entities,
            name=name,
            supported_language=supported_language,
            version=version,
            context=context,
        )

        logger.info(
            f"Initialized {self.name} with model={self.model_name}, "
            f"threshold={self.threshold}, device={self.map_location}"
        )

    def load(self) -> None:
        """Load the HuggingFace NER pipeline.

        :raises ImportError: If transformers library is not installed
        :raises ValueError: If model_name is not set
        """
        if not hf_pipeline:
            raise ImportError(
                "transformers is not installed. "
                "Install with: pip install transformers torch"
            )

        if not self.model_name:
            raise ValueError(
                "model_name must be set before calling load(). "
                "Pass it to __init__() or set it directly."
            )

        device = 0 if "cuda" in str(self.map_location).lower() else -1

        logger.info(f"Loading HuggingFace model: {self.model_name}")
        self.ner_pipeline = hf_pipeline(
            "token-classification",
            model=self.model_name,
            tokenizer=self.model_name,
            aggregation_strategy=self.aggregation_strategy,
            device=device,
            truncation=True,  # Handle long texts gracefully
        )
        logger.info(f"Successfully loaded {self.model_name}")

    def analyze(
        self,
        text: str,
        entities: List[str],
        nlp_artifacts: Optional[NlpArtifacts] = None,
    ) -> List[RecognizerResult]:
        """Analyze text for NER entities using HuggingFace model.

        This method intentionally ignores nlp_artifacts (spaCy results)
        to bypass tokenizer alignment issues.

        :param text: The text to analyze
        :param entities: List of entity types to detect
        :param nlp_artifacts: Ignored (spaCy artifacts not used)
        :return: List of RecognizerResult with detected entities
        """
        if not text or not text.strip():
            return []

        if not self.ner_pipeline:
            self.load()

        results = []

        try:
            predictions = self.ner_pipeline(text)
        except Exception as e:
            logger.warning(f"NER prediction failed: {e}")
            return []

        for pred in predictions:
            score = float(pred.get("score", 0))
            if score < self.threshold:
                continue

            # Map model label to Presidio entity
            model_label = pred.get("entity_group", pred.get("entity", ""))
            presidio_entity = self.label_mapping.get(model_label)

            if not presidio_entity:
                logger.debug(f"Skipping unmapped label: {model_label}")
                continue

            if entities and presidio_entity not in entities:
                continue

            explanation = AnalysisExplanation(
                recognizer=self.name,
                original_score=score,
                textual_explanation=(
                    f"Identified as {presidio_entity} by {self.model_name} "
                    f"(original label: {model_label})"
                ),
            )

            results.append(
                RecognizerResult(
                    entity_type=presidio_entity,
                    start=pred["start"],
                    end=pred["end"],
                    score=score,
                    analysis_explanation=explanation,
                )
            )

        return results
