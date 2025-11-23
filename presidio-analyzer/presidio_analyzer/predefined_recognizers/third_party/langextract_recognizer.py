import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional

import yaml

try:
    import langextract as lx
    LANGEXTRACT_AVAILABLE = True
except ImportError:
    LANGEXTRACT_AVAILABLE = False
    lx = None

try:
    from jinja2 import Template
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False
    Template = None

from presidio_analyzer import AnalysisExplanation, RecognizerResult
from presidio_analyzer.lm_recognizer import LMRecognizer

logger = logging.getLogger("presidio-analyzer")


class LangExtractRecognizer(LMRecognizer, ABC):
    """
    Base class for LangExtract-based PII recognizers.

    Subclasses implement _call_langextract() for specific LLM providers.
    """

    def __init__(self, config_path: str):
        """Initialize LangExtract recognizer."""
        if not LANGEXTRACT_AVAILABLE:
            raise ImportError(
                "LangExtract is not installed. "
                "Install it with: pip install presidio-analyzer[langextract]"
            )

        if not JINJA2_AVAILABLE:
            raise ImportError(
                "Jinja2 is not installed. "
                "Install it with: pip install jinja2"
            )

        # Load configuration file (provided by subclass)
        full_config = self._load_config_file(config_path)

        # Load LMRecognizer base configuration
        lm_config = full_config.get("lm_recognizer", {})

        # Load LangExtract-specific configuration
        self.config = full_config.get("langextract", {})

        if not self.config:
            raise ValueError(
                "Configuration file must contain 'langextract' section"
            )

        # Load model configuration from langextract.model section
        model_config = self.config.get("model", {})
        if not model_config:
            raise ValueError(
                "Configuration file must contain 'langextract.model' section"
            )

        # Extract model parameters and store as instance variables
        self.model_id = model_config.get("model_id")
        if not self.model_id:
            raise ValueError("Model configuration must contain 'model_id'")

        self.temperature = model_config.get("temperature")

        # Load all configuration from config file
        supported_entities = lm_config.get(
            "supported_entities"
        ) or self.config.get("supported_entities")
        if not supported_entities:
            raise ValueError(
                "Missing 'supported_entities' in "
                "lm_recognizer or langextract config"
            )

        min_score = lm_config.get("min_score", self.config.get("min_score", 0.5))

        # Get labels to ignore from lm_recognizer config (optional)
        labels_to_ignore = lm_config.get("labels_to_ignore", [])

        # Get generic consolidation flag from lm_recognizer (default True)
        enable_generic_consolidation = lm_config.get(
            "enable_generic_consolidation", True
        )

        super().__init__(
            supported_entities=supported_entities,
            supported_language="en",
            name="LangExtract LLM PII",
            version="1.0.0",
            model_id=self.model_id,
            temperature=self.temperature,
            min_score=min_score,
            labels_to_ignore=labels_to_ignore,
            enable_generic_consolidation=enable_generic_consolidation
        )

        # LangExtract-specific initialization
        self.prompt_template = self._load_prompt_file()
        self.examples = self._load_examples_file()
        self.entity_mappings = self._get_required_config("entity_mappings")
        self._presidio_to_langextract = {
            v: k for k, v in self.entity_mappings.items()
        }

        # Render the prompt with supported entities
        self.prompt_description = self._render_prompt()

        logger.info("Loaded recognizer: %s", self.name)

    def _load_config_file(self, config_path: str) -> Dict:
        """Load the entire YAML configuration file.

        :param config_path: Path to configuration file.
        :return: Full configuration dictionary.
        """
        config_path_obj = Path(config_path)

        if not config_path_obj.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {config_path}"
            )

        with open(config_path_obj, 'r') as f:
            return yaml.safe_load(f)

    def _load_config(
        self,
        config_path: Optional[str] = None,
        config_section: str = "langextract"
    ) -> Dict:
        """Load configuration section.

        Deprecated: Use _load_config_file for new code.
        """
        if config_path is None:
            config_path = self.DEFAULT_CONFIG_PATH

        full_config = self._load_config_file(config_path)
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

    def _render_prompt(self) -> str:
        """Render the Jinja2 prompt template with supported entities."""
        template = Template(self.prompt_template)

        # Get entity names from entity_mappings (LangExtract format)
        langextract_entities = sorted(set(self.entity_mappings.keys()))

        return template.render(
            supported_entities=self.supported_entities,
            langextract_entities=langextract_entities,
            entity_mappings=self.entity_mappings,
            enable_generic_consolidation=self.enable_generic_consolidation,
            labels_to_ignore=self.labels_to_ignore
        )

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

    def _call_llm(
        self,
        text: str,
        entities: List[str],
        **kwargs
    ):
        """Call LangExtract LLM and convert to RecognizerResult."""
        # Call provider-specific LangExtract implementation
        langextract_result = self._call_langextract(
            text=text,
            prompt=self.prompt_description,
            examples=self.examples
        )

        # Convert LangExtract extractions to RecognizerResult format
        results = []

        if not langextract_result or not langextract_result.extractions:
            return results

        for extraction in langextract_result.extractions:
            # Map LangExtract extraction_class to Presidio entity_type
            extraction_class = extraction.extraction_class.lower()
            entity_type = self.entity_mappings.get(extraction_class)

            if not entity_type:
                if self.enable_generic_consolidation:
                    # Pass through - consolidated by parent
                    entity_type = extraction_class.upper()
                    logger.debug(
                        "Unknown extraction class '%s' will be "
                        "consolidated to GENERIC_PII_ENTITY",
                        extraction_class,
                    )
                else:
                    # Generic consolidation disabled - skip unknown entities
                    logger.warning(
                        "Unknown extraction class '%s' not found in "
                        "entity mappings, skipping",
                        extraction_class,
                    )
                    continue

            if not extraction.char_interval:
                logger.warning("Extraction missing char_interval, skipping")
                continue

            # Calculate confidence score based on alignment status
            confidence = self._calculate_extraction_confidence(extraction)

            # Build metadata from extraction attributes and alignment
            metadata = {}
            if hasattr(extraction, 'attributes') and extraction.attributes:
                metadata['attributes'] = extraction.attributes
            if hasattr(extraction, 'alignment_status') and extraction.alignment_status:
                metadata['alignment'] = str(extraction.alignment_status)

            # Build analysis explanation
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

            # Create RecognizerResult
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
    def _call_langextract(
        self,
        text: str,
        prompt: str,
        examples: List,
        **kwargs
    ):
        """Call provider-specific LangExtract implementation.

        Subclasses implement this for specific providers (Ollama, OpenAI, etc.).
        """
        ...
