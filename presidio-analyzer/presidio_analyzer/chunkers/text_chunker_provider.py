"""Factory provider for creating text chunkers from configuration."""

import logging
from typing import Any, Dict, Optional, Type

from presidio_analyzer.chunkers.base_chunker import BaseTextChunker
from presidio_analyzer.chunkers.langchain_text_chunker import LangChainTextChunker

logger = logging.getLogger("presidio-analyzer")

# Registry mapping chunker type names to classes
_CHUNKER_REGISTRY: Dict[str, Type[BaseTextChunker]] = {
    "langchain": LangChainTextChunker,
}


class TextChunkerProvider:
    """Create text chunkers from configuration.

    :param chunker_configuration: Dict with chunker_type and optional params.
        Example::

            {"chunker_type": "langchain", "chunk_size": 300, "chunk_overlap": 75}

    If no configuration provided, uses langchain chunker with default params.
    Requires: pip install langchain-text-splitters
    """

    def __init__(
        self,
        chunker_configuration: Optional[Dict[str, Any]] = None,
    ):
        self.chunker_configuration = chunker_configuration or {
            "chunker_type": "langchain"
        }

    def create_chunker(self) -> BaseTextChunker:
        """Create a text chunker instance from configuration."""
        config = self.chunker_configuration.copy()
        chunker_type = config.pop("chunker_type", "langchain")

        if chunker_type not in _CHUNKER_REGISTRY:
            raise ValueError(
                f"Unknown chunker_type '{chunker_type}'. "
                f"Available: {list(_CHUNKER_REGISTRY.keys())}"
            )

        chunker_class = _CHUNKER_REGISTRY[chunker_type]
        return chunker_class(**config)

