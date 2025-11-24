import logging
from abc import ABC, abstractmethod
from typing import List

from presidio_analyzer.llm_utils import (
    check_langextract_available,
    convert_langextract_to_presidio_results,
    convert_to_langextract_format,
    extract_lm_config,
    get_model_config,
    get_supported_entities,
    load_prompt_file,
    load_yaml_examples,
    load_yaml_file,
    render_jinja_template,
    validate_config_fields,
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
        check_langextract_available()

        full_config = load_yaml_file(config_path)

        lm_config = extract_lm_config(full_config)
        langextract_config = full_config.get("langextract", {})

        supported_entities = get_supported_entities(lm_config, langextract_config)

        if not supported_entities:
            raise ValueError(
                "Configuration must contain 'supported_entities' in "
                "'lm_recognizer' or 'langextract'"
            )

        validate_config_fields(
            full_config,
            [
                ("langextract",),
                ("langextract", "model"),
                ("langextract", "model", "model_id"),
                ("langextract", "entity_mappings"),
                ("langextract", "prompt_file"),
                ("langextract", "examples_file"),
            ]
        )

        self.config = langextract_config
        model_config = get_model_config(
            full_config, provider_key="langextract"
        )
        self.model_id = model_config["model_id"]
        self.temperature = model_config.get("temperature")

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

        logger.info("Loaded recognizer: %s", self.name)

    def _call_llm(self, text: str, entities: List[str], **kwargs):
        """Call LangExtract LLM."""
        # Build extract params
        extract_params = {
            "text": text,
            "prompt": self.prompt_description,
            "examples": self.examples,
        }

        # Add temperature if configured
        if self.temperature is not None:
            extract_params["temperature"] = self.temperature

        # Add any additional kwargs
        extract_params.update(kwargs)

        langextract_result = self._call_langextract(**extract_params)

        return convert_langextract_to_presidio_results(
            langextract_result=langextract_result,
            entity_mappings=self.entity_mappings,
            supported_entities=self.supported_entities,
            enable_generic_consolidation=self.enable_generic_consolidation,
            recognizer_name=self.__class__.__name__
        )

    @abstractmethod
    def _call_langextract(self, **kwargs):
        """Call provider-specific LangExtract implementation."""
        ...
