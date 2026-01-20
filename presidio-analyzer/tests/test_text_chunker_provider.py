"""Tests for TextChunkerProvider factory pattern."""

import pytest

from presidio_analyzer.chunkers import (
    TextChunkerProvider,
    CharacterBasedTextChunker,
)


class TestTextChunkerProvider:
    """Test TextChunkerProvider."""

    def test_default_creates_character_chunker(self):
        """Default provider creates CharacterBasedTextChunker."""
        provider = TextChunkerProvider()
        chunker = provider.create_chunker()
        assert isinstance(chunker, CharacterBasedTextChunker)

    def test_custom_params_passed_to_chunker(self):
        """Custom parameters are passed to chunker."""
        provider = TextChunkerProvider(chunker_configuration={
            "chunker_type": "character",
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

    def test_character_chunker_type(self):
        """Provider creates CharacterBasedTextChunker when type is 'character'."""
        provider = TextChunkerProvider(chunker_configuration={
            "chunker_type": "character",
            "chunk_size": 300,
        })
        chunker = provider.create_chunker()
        assert isinstance(chunker, CharacterBasedTextChunker)
        assert chunker.chunk_size == 300

