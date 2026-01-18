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

import copy
import logging
from typing import Dict, List, Optional, Union

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
        chunk_overlap_size: int = 40,
        chunk_size: int = 400,
        batch_size: int = 1,
        max_text_length: Optional[int] = None,
        device: Optional[Union[str, int]] = None,
        tokenizer_name: Optional[str] = None,
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
            ("simple", "first", "average", "max").
            Recommendation: Use "simple" or "first" so that entities are pre-aggregated
            by the model, preserving performance and alignment.
        :param chunk_overlap_size: Number of overlapping characters in each chunk.
            Defaults to 40.
        :param chunk_size: Size of text chunks (in characters). Defaults to 400.
        :param batch_size: Batch size for inference. Defaults to 1.
        :param max_text_length: Maximum allowed text length. If exceeded,
            text is truncated. Defaults to None (no limit).
        :param device: Device to use. Accepts:
            - "cpu" or -1 for CPU
            - "cuda" or "cuda:N" or int N for GPU
            - None for auto-detection (GPU if available, else CPU)
            Defaults to None.
        :param tokenizer_name: Name of the tokenizer to use. Defaults to model_name.
        """
        self.model_name = model_name
        self.tokenizer_name = tokenizer_name or model_name
        self.label_mapping = label_mapping or self.DEFAULT_LABEL_MAPPING
        self.threshold = threshold
        self.aggregation_strategy = aggregation_strategy
        if self.aggregation_strategy == "none":
            logger.warning(
                "aggregation_strategy='none' may result in fragmented entities "
                "(e.g., 'B-PER', 'I-PER'). Recommended: 'simple' or 'first'."
            )
        self.chunk_overlap_size = chunk_overlap_size
        self.chunk_size = chunk_size
        self.batch_size = batch_size
        self.max_text_length = max_text_length
        self.device = device
        self.ner_pipeline = None

        # Derive supported entities from label mapping
        if supported_entities:
            final_supported_entities = supported_entities
        else:
            # Use sorted set for deterministic order
            final_supported_entities = sorted(list(set(self.label_mapping.values())))

        super().__init__(
            supported_entities=final_supported_entities,
            name=name,
            supported_language=supported_language,
            version=version,
            context=context,
        )

        if self.chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if self.chunk_overlap_size < 0:
            raise ValueError("chunk_overlap_size must be non-negative")

        if self.chunk_size <= self.chunk_overlap_size:
            raise ValueError(
                "chunk_overlap_size must be smaller than chunk_size"
            )

        logger.info(
            f"Initialized {self.name} with model={self.model_name}, "
            f"threshold={self.threshold}, device={self.device}"
        )

    def load(self) -> None:
        """Load the HuggingFace NER pipeline.

        :raises ImportError: If transformers library is not installed
        :raises ValueError: If model_name is not set
        """
        if self.ner_pipeline is not None:
            return

        if hf_pipeline is None:
            raise ImportError(
                "transformers is not installed. "
                "Install with: pip install transformers torch"
            )

        if not self.model_name:
            raise ValueError(
                "model_name must be set before calling load(). "
                "Pass it to __init__() or set it directly."
            )

        device = -1
        device_str = str(self.device).lower() if self.device else ""

        if isinstance(self.device, int):
            device = self.device
        elif "cpu" in device_str:
            device = -1
        elif "cuda" in device_str:
            if ":" in device_str:
                try:
                    device = int(device_str.split(":")[1])
                except ValueError:
                    device = 0
            else:
                device = 0  # Default to first GPU if just "cuda" is passed
        elif self.device is None:
            # Auto-detect: Use GPU if available, else CPU
            device = device_detector.get_device()

        logger.info(f"Loading HuggingFace model: {self.model_name}, device={device}")

        self.ner_pipeline = hf_pipeline(
            "token-classification",
            model=self.model_name,
            tokenizer=self.tokenizer_name,
            aggregation_strategy=self.aggregation_strategy,
            device=device,
        )
        logger.info(f"Successfully loaded {self.model_name}")

    def _get_ner_results_for_text(self, text: str) -> List[dict]:
        """Run model inference on text, chunking if necessary."""
        # Calculate inputs based on the text
        text_length = len(text)

        # 1. Split text into chunks
        # Note: We chunk even short texts to ensure consistent deduplication logic
        logger.debug(
            f"Splitting text into chunks: length {text_length}"
        )
        predictions = []
        chunk_indexes = HuggingFaceNerRecognizer.split_text_to_char_chunks(
            text_length, self.chunk_size, self.chunk_overlap_size
        )

        # 2. Iterate over chunks and run inference
        chunk_texts = [text[start:end] for start, end in chunk_indexes]

        # Use batch processing for efficiency with fallback for older versions
        try:
            batch_preds = self.ner_pipeline(
                chunk_texts, batch_size=self.batch_size, truncation=True
            )
        except (TypeError, ValueError, RuntimeError) as e:
            # Fallback: older pipeline versions may not accept batch_size/truncation
            logger.debug(f"Batch processing failed, falling back to iterative: {e}")
            batch_preds = [
                self.ner_pipeline(chunk_text) for chunk_text in chunk_texts
            ]

        for i, chunk_preds in enumerate(batch_preds):
            chunk_start = chunk_indexes[i][0]

            # Align indexes: add chunk_start to start/end positions
            for prediction in chunk_preds:
                # Use deepcopy to ensure full object safety
                aligned_pred = copy.deepcopy(prediction)
                aligned_pred["start"] += chunk_start
                aligned_pred["end"] += chunk_start
                predictions.append(aligned_pred)

        # 3. Remove duplicates
        # Overlapping chunks might detect the same entity twice.
        # We keep the one with the highest confidence score.
        deduplicated = {}
        for pred in predictions:
            # Handle both 'entity_group' (aggregation) and 'entity' (token level)
            raw_label = pred.get("entity_group", pred.get("entity"))
            label = HuggingFaceNerRecognizer._normalize_label(raw_label)

            # Key using Presidio entity for semantic deduplication.
            # Different model labels mapping to the same Presidio entity
            # are considered duplicates; we keep the higher score.
            presidio_entity = self.label_mapping.get(label)
            if not presidio_entity:
                continue

            key = (pred["start"], pred["end"], presidio_entity)

            if key not in deduplicated:
                deduplicated[key] = pred
            else:
                # If existing score is lower, replace it
                if deduplicated[key]["score"] < pred["score"]:
                    deduplicated[key] = pred

        return list(deduplicated.values())

    @staticmethod
    def _normalize_label(label: str) -> str:
        """Normalize label by removing B-/I- prefix.

        Some models return BIO-format labels (e.g., "B-PER", "I-PER") even with
        aggregation_strategy="simple". This method strips the prefix so that
        label_mapping can correctly map to Presidio entities.

        Example: "B-PER" -> "PER" -> mapped to "PERSON"
        """
        if isinstance(label, str):
            if label.startswith("B-") or label.startswith("I-"):
                return label[2:]
        return label

    @staticmethod
    def split_text_to_char_chunks(
        input_length: int, chunk_length: int, overlap_length: int
    ) -> List[List[int]]:
        """Calculate chunks of text with size chunk_length.

        Each chunk has overlap_length number of characters to create
        context and continuity for the model.

        :param input_length: Length of input text
        :param chunk_length: Length of each chunk
        :param overlap_length: Number of overlapping characters
        :return: List of [start, end] positions for chunks
        """
        if chunk_length <= 0:
            raise ValueError("chunk_length must be positive")
        if overlap_length < 0:
            raise ValueError("overlap_length must be non-negative")

        if input_length <= chunk_length:
            return [[0, input_length]]

        return [
            [i, min(i + chunk_length, input_length)]
            for i in range(
                0, input_length - overlap_length, chunk_length - overlap_length
            )
        ]

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

        if self.max_text_length and len(text) > self.max_text_length:
            logger.warning(
                f"Text length ({len(text)}) exceeds max_text_length "
                f"({self.max_text_length}). Truncating."
            )
            text = text[: self.max_text_length]

        if not self.ner_pipeline:
            self.load()

        results = []

        try:
            # Get NER predictions with chunking and deduplication
            predictions = self._get_ner_results_for_text(text)
        except Exception as e:
            logger.warning(f"NER prediction failed: {e}", exc_info=True)
            return []

        for pred in predictions:
            raw_label = pred.get("entity_group", pred.get("entity"))
            model_label = HuggingFaceNerRecognizer._normalize_label(raw_label)

            presidio_entity = self.label_mapping.get(model_label)
            if not presidio_entity:
                continue

            if pred["score"] < self.threshold:
                continue

            if entities and presidio_entity not in entities:
                continue

            score = float(pred.get("score", 0))
            textual_explanation = (
                f"Identified as {presidio_entity} by {self.model_name} "
                f"(original label: {model_label})"
            )

            explanation = AnalysisExplanation(
                recognizer=self.name,
                original_score=score,
                textual_explanation=textual_explanation,
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
