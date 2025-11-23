import logging
from abc import ABC, abstractmethod
from typing import Dict, List

try:
    import langextract as lx
    LANGEXTRACT_AVAILABLE = True
except ImportError:
    LANGEXTRACT_AVAILABLE = False
    lx = None

from presidio_analyzer import AnalysisExplanation, RecognizerResult
from presidio_analyzer.llm_utils import (
    convert_to_langextract_format,
    extract_lm_config,
    get_model_config,
    load_prompt_file,
    load_yaml_config,
    load_yaml_examples,
    render_jinja_template,
)
from presidio_analyzer.lm_recognizer import LMRecognizer

logger = logging.getLogger("presidio-analyzer")


class LangExtractRecognizer(LMRecognizer, ABC):
    """
    Base class for LangExtract-based PII recognizers.

    Subclasses implement _call_langextract() for specific LLM providers.
    """

    def __init__(self, config_path: str, name: str = "LangExtract LLM PII"):
        """Initialize LangExtract recognizer.

        :param config_path: Path to configuration file.
        :param name: Name of the recognizer (provided by subclass).
        """
        if not LANGEXTRACT_AVAILABLE:
            raise ImportError(
                "LangExtract is not installed. "
                "Install it with: pip install presidio-analyzer[langextract]"
            )

        # Load configuration
        full_config = load_yaml_config(config_path)
        self._validate_config(full_config)

        lm_config = extract_lm_config(full_config)
        langextract_config = full_config.get("langextract", {})

        self.config = langextract_config
        model_config = get_model_config(
            full_config, provider_key="langextract"
        )
        self.model_id = model_config["model_id"]
        self.temperature = model_config.get("temperature")

        # Get supported entities from either lm_config or langextract_config
        supported_entities = (
            lm_config.get("supported_entities")
            or langextract_config.get("supported_entities")
        )

        super().__init__(
            supported_entities=supported_entities,
            supported_language="en",
            name=name,
            version="1.0.0",
            model_id=self.model_id,
            temperature=self.temperature,
            min_score=lm_config.get("min_score"),
            labels_to_ignore=lm_config.get("labels_to_ignore"),
            enable_generic_consolidation=lm_config.get(
                "enable_generic_consolidation"
            ),
        )

        # Load examples and render prompt
        examples_data = load_yaml_examples(
            langextract_config["examples_file"]
        )
        self.examples = convert_to_langextract_format(examples_data)

        prompt_template = load_prompt_file(
            langextract_config["prompt_file"]
        )
        self.prompt_description = render_jinja_template(
            prompt_template,
            supported_entities=self.supported_entities,
            enable_generic_consolidation=self.enable_generic_consolidation,
            labels_to_ignore=self.labels_to_ignore,
        )

        self.entity_mappings = langextract_config["entity_mappings"]
        self._presidio_to_langextract = {
            v: k for k, v in self.entity_mappings.items()
        }
        self._supported_entities_set = set(supported_entities)

        logger.info("Loaded recognizer: %s", self.name)

    def _validate_config(self, config: Dict) -> None:
        """Validate configuration structure and required fields.

        :param config: Full configuration dictionary.
        """
        lm_config = config.get("lm_recognizer", {})
        langextract_config = config.get("langextract", {})

        if not langextract_config:
            raise ValueError("Configuration must contain 'langextract' section")

        model_config = langextract_config.get("model", {})
        if not model_config:
            raise ValueError(
                "Configuration 'langextract' must contain 'model' section"
            )

        if not model_config.get("model_id"):
            raise ValueError(
                "Configuration 'langextract.model' must contain 'model_id'"
            )

        if not lm_config.get("supported_entities") and not langextract_config.get(
            "supported_entities"
        ):
            raise ValueError(
                "Configuration must contain 'supported_entities' in "
                "'lm_recognizer' or 'langextract'"
            )

        if not langextract_config.get("entity_mappings"):
            raise ValueError(
                "Configuration 'langextract' must contain 'entity_mappings'"
            )

    def _call_llm(self, text: str, entities: List[str], **kwargs):
        """Call LangExtract LLM and convert to RecognizerResult."""
        langextract_result = self._call_langextract(
            text=text,
            prompt=self.prompt_description,
            examples=self.examples
        )

        results = []
        if not langextract_result or not langextract_result.extractions:
            return results

        for extraction in langextract_result.extractions:
            extraction_class = extraction.extraction_class

            if extraction_class in self._supported_entities_set:
                entity_type = extraction_class
            else:
                extraction_class_lower = extraction_class.lower()
                entity_type = self.entity_mappings.get(extraction_class_lower)

            if not entity_type:
                if self.enable_generic_consolidation:
                    entity_type = extraction_class.upper()
                    logger.debug(
                        "Unknown extraction class '%s' will be consolidated to "
                        "GENERIC_PII_ENTITY",
                        extraction_class,
                    )
                else:
                    logger.warning(
                        "Unknown extraction class '%s' not found in entity "
                        "mappings, skipping",
                        extraction_class,
                    )
                    continue

            if not extraction.char_interval:
                logger.warning("Extraction missing char_interval, skipping")
                continue

            confidence = self._calculate_extraction_confidence(extraction)

            metadata = {}
            if hasattr(extraction, 'attributes') and extraction.attributes:
                metadata['attributes'] = extraction.attributes
            if hasattr(extraction, 'alignment_status') and extraction.alignment_status:
                metadata['alignment'] = str(extraction.alignment_status)

            explanation = AnalysisExplanation(
                recognizer=self.__class__.__name__,
                original_score=confidence,
                textual_explanation=(
                    f"LangExtract extraction with "
                    f"{extraction.alignment_status} alignment"
                    if hasattr(extraction, "alignment_status")
                    and extraction.alignment_status
                    else "LangExtract extraction"
                ),
            )

            result = RecognizerResult(
                entity_type=entity_type,
                start=extraction.char_interval.start_pos,
                end=extraction.char_interval.end_pos,
                score=confidence,
                analysis_explanation=explanation,
                recognition_metadata=metadata if metadata else None
            )

            results.append(result)

        return results

    def _calculate_extraction_confidence(self, extraction) -> float:
        """Calculate confidence score from LangExtract extraction."""
        default_score = 0.85

        if not hasattr(extraction, "alignment_status") or not (
            extraction.alignment_status
        ):
            return default_score

        alignment_scores = {
            "MATCH_EXACT": 0.95,
            "MATCH_FUZZY": 0.80,
            "MATCH_LESSER": 0.70,
            "NOT_ALIGNED": 0.60,
        }

        status = str(extraction.alignment_status).upper()
        for status_key, score in alignment_scores.items():
            if status_key in status:
                return score

        return default_score

    @abstractmethod
    def _call_langextract(self, text: str, prompt: str, examples: List, **kwargs):
        """Call provider-specific LangExtract implementation.

        Subclasses implement this for specific providers (Ollama, OpenAI, etc.).
        """
        ...
