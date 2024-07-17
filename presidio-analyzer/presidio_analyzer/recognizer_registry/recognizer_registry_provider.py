from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, Optional, Union

from presidio_analyzer.recognizer_registry import RecognizerRegistry
from presidio_analyzer.recognizer_registry.recognizers_loader_utils import (
    RecognizerConfigurationLoader,
    RecognizerListLoader,
)

logger = logging.getLogger("presidio-analyzer")


class RecognizerRegistryProvider:
    r"""
    Utility class for loading Recognizer Registry.

    Use this class to load recognizer registry from a yaml file

    :param conf_file: Path to yaml file containing registry configuration
    :param registry_configuration: Dict containing registry configuration
    :example:
        {
            "supported_languages": ["de", "es"],
            "recognizers": [
                {
                    "name": "Zip code Recognizer",
                    "supported_language": "en",
                    "patterns": [
                        {
                            "name": "zip code (weak)",
                            "regex": "(\\b\\d{5}(?:\\-\\d{4})?\\b)",
                            "score": 0.01,
                        }
                    ],
                    "context": ["zip", "code"],
                    "supported_entity": "ZIP",
                }
            ]
        }
    """

    def __init__(
        self,
        conf_file: Optional[Union[Path, str]] = None,
        registry_configuration: Optional[Dict] = None,
    ):
        self.configuration = RecognizerConfigurationLoader.get(
            conf_file=conf_file, registry_configuration=registry_configuration
        )
        return

    def create_recognizer_registry(self) -> RecognizerRegistry:
        """Create a recognizer registry according to configuration loaded previously."""
        supported_languages = self.configuration.get("supported_languages")
        global_regex_flags = self.configuration.get("global_regex_flags")
        recognizers = RecognizerListLoader.get(
            self.configuration.get("recognizers"),
            supported_languages,
            global_regex_flags,
        )

        return RecognizerRegistry(
            recognizers=recognizers,
            supported_languages=supported_languages,
            global_regex_flags=global_regex_flags,
        )
