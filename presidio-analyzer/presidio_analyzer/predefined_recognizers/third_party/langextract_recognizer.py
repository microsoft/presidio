import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

import yaml

try:
    import langextract as lx
    LANGEXTRACT_AVAILABLE = True
except ImportError:
    LANGEXTRACT_AVAILABLE = False
    lx = None

from presidio_analyzer import AnalysisExplanation, RecognizerResult, RemoteRecognizer
from presidio_analyzer.nlp_engine import NlpArtifacts

logger = logging.getLogger("presidio-analyzer")


class LangExtractRecognizer(RemoteRecognizer):
    """PII detection using LangExtract with Ollama local models."""

    DEFAULT_CONFIG_PATH = Path(__file__).parent.parent.parent / "conf" / "langextract_config.yaml"

    def __init__(
        self,
        supported_entities: Optional[List[str]] = None,
        supported_language: str = "en",
        config_path: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize LangExtract recognizer with Ollama.

        :param supported_entities: List of PII entities to detect.
        :param supported_language: Language code (only 'en' supported).
        :param config_path: Path to YAML configuration file.
        :param kwargs: Additional arguments for parent class.
        """
        if not LANGEXTRACT_AVAILABLE:
            raise ImportError(
                "LangExtract is not installed. "
                "Install it with: pip install presidio-analyzer[langextract]"
            )

        self.config = self._load_config(config_path)

        if not self.config.get("enabled", False):
            logger.info("LangExtract recognizer disabled")
            self.enabled = False
        else:
            self.enabled = True

        if supported_entities is None:
            supported_entities = self.config.get("supported_entities", [])

        super().__init__(
            supported_entities=supported_entities,
            supported_language=supported_language,
            name="LangExtract LLM PII",
            version="1.0.0",
            **kwargs
        )

        self.prompt_description = self._load_prompt_file()
        self.examples = self._load_examples_file()
        self.entity_mappings = self.config.get("entity_mappings", {})
        self._presidio_to_langextract = {
            v: k for k, v in self.entity_mappings.items()
        }

        # Ollama configuration (local models only)
        self.model_id = self.config.get("model_id", "llama3.2:3b")
        self.model_url = self.config.get("model_url", "http://localhost:11434")
        self.temperature = self.config.get("temperature")
        self.min_score = self.config.get("min_score", 0.5)

        logger.info("Loaded recognizer: %s", self.name)

    def _load_config(self, config_path: Optional[str] = None) -> Dict:
        if config_path is None:
            config_path = self.DEFAULT_CONFIG_PATH

        config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(
                f"LangExtract configuration file not found: {config_path}"
            )

        with open(config_path, 'r') as f:
            full_config = yaml.safe_load(f)

        langextract_config = full_config.get("langextract", {})

        if not langextract_config:
            raise ValueError(
                "Configuration file must contain 'langextract' section"
            )

        return langextract_config

    def _load_prompt_file(self) -> str:
        prompt_file = self.config.get("prompt_file")
        if not prompt_file:
            raise ValueError("Configuration must specify 'prompt_file'")

        prompt_path = Path(__file__).parent.parent.parent / "conf" / prompt_file

        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

        with open(prompt_path, 'r') as f:
            return f.read()

    def _load_examples_file(self) -> List:
        examples_file = self.config.get("examples_file")
        if not examples_file:
            raise ValueError("Configuration must specify 'examples_file'")

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
        if not self.enabled:
            return []

        if not text or not text.strip():
            return []

        if entities:
            if not any(entity in self.supported_entities for entity in entities):
                return []

        try:
            extract_params = {
                "text_or_documents": text,
                "prompt_description": self.prompt_description,
                "examples": self.examples,
                "model_id": self.model_id,
            }

            # Ollama-specific parameters
            extract_params["model_url"] = self.model_url
            if self.temperature is not None:
                extract_params["temperature"] = self.temperature

            result = lx.extract(**extract_params)

            return self._convert_to_recognizer_results(result, entities)

        except Exception as e:
            logger.error("LangExtract extraction failed: %s", str(e))
            return []

    def _convert_to_recognizer_results(
        self,
        langextract_result,
        requested_entities: Optional[List[str]] = None
    ) -> List[RecognizerResult]:
        recognizer_results = []

        if not langextract_result or not langextract_result.extractions:
            return recognizer_results

        for extraction in langextract_result.extractions:
            extraction_class = extraction.extraction_class.lower()
            entity_type = self.entity_mappings.get(extraction_class)

            if not entity_type:
                continue

            if requested_entities and entity_type not in requested_entities:
                continue

            if not extraction.char_interval:
                continue

            start = extraction.char_interval.start_pos
            end = extraction.char_interval.end_pos

            score = self._calculate_score(extraction)

            if score < self.min_score:
                continue

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

    def _calculate_score(self, extraction) -> float:
        default_score = 0.85

        if not hasattr(extraction, 'alignment_status') or not extraction.alignment_status:
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

    def _build_explanation(
        self,
        extraction,
        entity_type: str
    ) -> AnalysisExplanation:
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

    def get_supported_entities(self) -> List[str]:
        """Return list of supported PII entity types."""
        return self.supported_entities
