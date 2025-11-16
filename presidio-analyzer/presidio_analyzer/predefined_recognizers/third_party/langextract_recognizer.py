import logging
from abc import abstractmethod
from pathlib import Path
from typing import Dict, List, Optional

import yaml

try:
    import langextract as lx
    LANGEXTRACT_AVAILABLE = True
except ImportError:
    LANGEXTRACT_AVAILABLE = False
    lx = None

from presidio_analyzer import AnalysisExplanation, RecognizerResult
from presidio_analyzer.lm_recognizer import LMRecognizer
from presidio_analyzer.nlp_engine import NlpArtifacts

logger = logging.getLogger("presidio-analyzer")


class LangExtractRecognizer(LMRecognizer):
    """
    Abstract base class for PII detection using LangExtract library.

    Handles LangExtract-specific functionality including:
    - Configuration loading and validation
    - Examples and prompt management
    - Entity mapping between LangExtract and Presidio
    - Result conversion from LangExtract format to RecognizerResult

    Note: This is an abstract class. Concrete implementations
    (like OllamaLangExtractRecognizer) must define their own
    DEFAULT_CONFIG_PATH.
    """

    # No DEFAULT_CONFIG_PATH here - subclasses must define their own

    def __init__(
        self,
        supported_entities: Optional[List[str]] = None,
        supported_language: str = "en",
        config_path: Optional[str] = None,
        name: str = "LangExtract LLM PII",
        version: str = "1.0.0",
        model_id: Optional[str] = None,
        temperature: Optional[float] = None,
        min_score: Optional[float] = None,
        **kwargs
    ):
        """
        Initialize LangExtract recognizer base class.

        :param supported_entities: List of PII entities to detect.
        :param supported_language: Language code (only 'en' supported).
        :param config_path: Path to YAML configuration file.
        :param name: Recognizer name.
        :param version: Recognizer version.
        :param model_id: Language model identifier (from subclass).
        :param temperature: Model temperature (from subclass).
        :param min_score: Minimum confidence score (from subclass).
        :param kwargs: Additional arguments for parent class.
        """
        if not LANGEXTRACT_AVAILABLE:
            raise ImportError(
                "LangExtract is not installed. "
                "Install it with: pip install presidio-analyzer[langextract]"
            )

        # Load shared LangExtract configuration
        self.config = self._load_config(config_path, "langextract")

        if supported_entities is None:
            supported_entities = self._get_required_config("supported_entities")

        if min_score is None:
            min_score = self._get_required_config("min_score")

        super().__init__(
            supported_entities=supported_entities,
            supported_language=supported_language,
            name=name,
            version=version,
            model_id=model_id,
            temperature=temperature,
            min_score=min_score,
            **kwargs
        )

        # LangExtract-specific initialization
        self.prompt_description = self._load_prompt_file()
        self.examples = self._load_examples_file()
        self.entity_mappings = self._get_required_config("entity_mappings")
        self._presidio_to_langextract = {
            v: k for k, v in self.entity_mappings.items()
        }

        logger.info("Loaded recognizer: %s", self.name)

    def _load_config(
        self,
        config_path: Optional[str] = None,
        config_section: str = "langextract"
    ) -> Dict:
        """Load and validate LangExtract configuration.

        :param config_path: Path to configuration file.
        :param config_section: Name of the config section
            (e.g., "ollama", "langextract").
        :return: Configuration dictionary.
        """
        if config_path is None:
            config_path = self.DEFAULT_CONFIG_PATH

        config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(
                f"LangExtract configuration file not found: {config_path}"
            )

        with open(config_path, 'r') as f:
            full_config = yaml.safe_load(f)

        section_config = full_config.get(config_section, {})

        if not section_config:
            raise ValueError(
                f"Configuration file must contain '{config_section}' section"
            )

        return section_config

    def _get_required_config(self, key: str):
        """Get required configuration value or raise error if missing."""
        value = self.config.get(key)
        if value is None:
            raise ValueError(
                f"Missing required configuration '{key}' in configuration file"
            )
        return value

    def _load_prompt_file(self) -> str:
        """Load the prompt template from configuration."""
        prompt_file = self._get_required_config("prompt_file")
        prompt_path = Path(__file__).parent.parent.parent / "conf" / prompt_file

        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

        with open(prompt_path, 'r') as f:
            return f.read()

    def _load_examples_file(self) -> List:
        """Load and convert examples from YAML to LangExtract format."""
        examples_file = self._get_required_config("examples_file")
        examples_path = Path(__file__).parent.parent.parent / "conf" / examples_file

        if not examples_path.exists():
            raise FileNotFoundError(f"Examples file not found: {examples_path}")

        with open(examples_path, 'r') as f:
            data = yaml.safe_load(f)

        examples_data = data.get("examples", [])
        if not examples_data:
            raise ValueError("Examples file must contain 'examples' list")

        return self._convert_to_langextract_examples(examples_data)

    def _convert_to_langextract_examples(self, examples_data: List[Dict]) -> List:
        """Convert YAML examples to LangExtract objects."""
        langextract_examples = []
        for example in examples_data:
            extractions = [
                lx.data.Extraction(
                    extraction_class=ext["extraction_class"],
                    extraction_text=ext["extraction_text"],
                    attributes=ext.get("attributes", {})
                )
                for ext in example.get("extractions", [])
            ]

            langextract_examples.append(
                lx.data.ExampleData(
                    text=example["text"],
                    extractions=extractions
                )
            )

        return langextract_examples

    def _parse_llm_response(
        self,
        response,
        original_text: str
    ) -> List:
        """
        Parse LangExtract response into structured format.

        :param response: LangExtract result object.
        :param original_text: Original text that was analyzed.
        :return: List of extractions from LangExtract.
        """
        if not response or not response.extractions:
            return []
        return response.extractions

    def analyze(
        self,
        text: str,
        entities: Optional[List[str]] = None,
        nlp_artifacts: Optional[NlpArtifacts] = None
    ) -> List[RecognizerResult]:
        """
        Analyze text for PII using LangExtract.

        :param text: Text to analyze.
        :param entities: Entity types to detect (optional).
        :param nlp_artifacts: Not used.
        :return: List of detected PII entities.
        """
        if not text or not text.strip():
            logger.debug("Empty text provided, returning empty results")
            return []

        if entities:
            if not any(entity in self.supported_entities for entity in entities):
                logger.debug(
                    "No requested entities (%s) match supported entities (%s)",
                    entities, self.supported_entities
                )
                return []

        try:
            # Call the LLM through the abstract method
            result = self._call_llm(
                text=text,
                prompt=self.prompt_description,
                examples=self.examples
            )

            converted_results = self._convert_to_recognizer_results(result, entities)
            if converted_results:
                logger.info("LangExtract found %d PII entities", len(converted_results))

            return converted_results

        except Exception as e:
            logger.error("LangExtract extraction failed: %s", str(e), exc_info=True)
            return []

    def _convert_to_recognizer_results(
        self,
        langextract_result,
        requested_entities: Optional[List[str]] = None
    ) -> List[RecognizerResult]:
        """Convert LangExtract results to Presidio RecognizerResult format."""
        recognizer_results = []

        extractions = self._parse_llm_response(langextract_result, "")
        if not extractions:
            return recognizer_results

        for extraction in extractions:
            extraction_class = extraction.extraction_class.lower()
            entity_type = self.entity_mappings.get(extraction_class)

            if not entity_type:
                logger.warning(
                    "Unknown extraction class '%s' not found in entity mappings",
                    extraction_class
                )
                continue

            if requested_entities and entity_type not in requested_entities:
                continue

            if not extraction.char_interval:
                logger.warning("Extraction missing char_interval, skipping")
                continue

            score = self._calculate_score(extraction)
            if score < self.min_score:
                continue

            start = extraction.char_interval.start_pos
            end = extraction.char_interval.end_pos
            explanation = self._build_explanation(extraction, entity_type)

            recognizer_result = RecognizerResult(
                entity_type=entity_type,
                start=start,
                end=end,
                score=score,
                analysis_explanation=explanation,
            )

            recognizer_results.append(recognizer_result)

        return recognizer_results

    def _calculate_confidence_score(self, extraction_info: Dict) -> float:
        """
        Calculate confidence score for a LangExtract extraction.

        :param extraction_info: LangExtract extraction object.
        :return: Confidence score between 0 and 1.
        """
        extraction = extraction_info
        default_score = 0.85

        if not hasattr(extraction, 'alignment_status') or not (
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

    def _calculate_score(self, extraction) -> float:
        """Legacy method - delegates to _calculate_confidence_score."""
        return self._calculate_confidence_score(extraction)

    def _build_explanation(
        self,
        extraction,
        entity_type: str
    ) -> AnalysisExplanation:
        """Build explanation for a LangExtract extraction result."""
        attributes_text = ""
        if hasattr(extraction, 'attributes') and extraction.attributes:
            attr_parts = [f"{k}={v}" for k, v in extraction.attributes.items()]
            attributes_text = f" ({', '.join(attr_parts)})"

        textual_explanation = (
            f"Identified as {entity_type} by LangExtract LLM "
            f"using {self.model_id}{attributes_text}"
        )

        explanation = AnalysisExplanation(
            recognizer=self.__class__.__name__,
            original_score=1.0,
            textual_explanation=textual_explanation,
        )

        return explanation

    @abstractmethod
    def _call_llm(
        self,
        text: str,
        prompt: str,
        examples: List,
        **kwargs
    ):
        """
        Call the specific LLM implementation with LangExtract.

        :param text: Text to analyze.
        :param prompt: Prompt description for LangExtract.
        :param examples: LangExtract examples.
        :param kwargs: Additional LLM-specific parameters.
        :return: LangExtract result object.
        """
        ...

    def get_supported_entities(self) -> List[str]:
        """Return list of supported PII entity types."""
        return self.supported_entities
