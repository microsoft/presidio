"""Tests for TextChunkerProvider factory pattern."""

import pytest

from presidio_analyzer.chunkers import (
    TextChunkerProvider,
    LangChainTextChunker,
)


class TestTextChunkerProvider:
    """Test TextChunkerProvider."""

    def test_default_creates_langchain_chunker(self):
        """Default provider creates LangChainTextChunker."""
        provider = TextChunkerProvider()
        chunker = provider.create_chunker()
        assert isinstance(chunker, LangChainTextChunker)

    def test_custom_params_passed_to_chunker(self):
        """Custom parameters are passed to chunker."""
        provider = TextChunkerProvider(chunker_configuration={
            "chunker_type": "langchain",
            "chunk_size": 500,
            "chunk_overlap": 100,
        })
        chunker = provider.create_chunker()
        assert chunker._chunk_size == 500
        assert chunker._chunk_overlap == 100

    def test_unknown_chunker_type_raises_error(self):
        """Unknown chunker_type raises ValueError."""
        provider = TextChunkerProvider(chunker_configuration={
            "chunker_type": "unknown"
        })
        with pytest.raises(ValueError, match="Unknown chunker_type"):
            provider.create_chunker()

    def test_langchain_chunker_type(self):
        """Provider creates LangChainTextChunker when type is 'langchain'."""
        provider = TextChunkerProvider(chunker_configuration={
            "chunker_type": "langchain",
            "chunk_size": 300,
        })
        chunker = provider.create_chunker()
        assert isinstance(chunker, LangChainTextChunker)
        assert chunker.chunk_size == 300

