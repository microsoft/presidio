"""Tests for LangChainTextChunker."""

import pytest

from presidio_analyzer.chunkers import LangChainTextChunker, TextChunk


class TestLangChainTextChunkerInit:
    """Tests for LangChainTextChunker initialization."""

    def test_default_values(self):
        """Test default initialization values."""
        chunker = LangChainTextChunker()
        assert chunker.chunk_size == 250
        assert chunker.chunk_overlap == 50

    def test_custom_chunk_size(self):
        """Test custom chunk size."""
        chunker = LangChainTextChunker(chunk_size=100, chunk_overlap=10)
        assert chunker.chunk_size == 100

    def test_custom_chunk_overlap(self):
        """Test custom chunk overlap."""
        chunker = LangChainTextChunker(chunk_size=100, chunk_overlap=20)
        assert chunker.chunk_overlap == 20

    def test_invalid_chunk_size_zero(self):
        """Test that zero chunk_size raises ValueError."""
        with pytest.raises(ValueError):
            LangChainTextChunker(chunk_size=0)

    def test_invalid_chunk_size_negative(self):
        """Test that negative chunk_size raises ValueError."""
        with pytest.raises(ValueError):
            LangChainTextChunker(chunk_size=-10)


class TestLangChainTextChunkerChunk:
    """Tests for LangChainTextChunker.chunk() method."""

    def test_empty_text(self):
        """Test chunking empty text returns empty list."""
        chunker = LangChainTextChunker(chunk_size=50, chunk_overlap=10)
        assert chunker.chunk("") == []

    def test_short_text_single_chunk(self):
        """Test text shorter than chunk_size returns single chunk."""
        chunker = LangChainTextChunker(chunk_size=100, chunk_overlap=10)
        text = "Hello world"
        chunks = chunker.chunk(text)

        assert len(chunks) == 1
        assert chunks[0].text == text
        assert chunks[0].start == 0
        assert chunks[0].end == len(text)

    def test_splits_on_paragraph(self):
        """Test splitting on paragraph separator (\\n\\n)."""
        chunker = LangChainTextChunker(chunk_size=30, chunk_overlap=10)
        text = "First paragraph.\n\nSecond paragraph."
        chunks = chunker.chunk(text)

        assert len(chunks) == 2
        assert "First paragraph" in chunks[0].text
        assert "Second paragraph" in chunks[1].text

    def test_splits_on_newline(self):
        """Test splitting on newline when paragraphs too large."""
        chunker = LangChainTextChunker(chunk_size=20, chunk_overlap=10)
        text = "Line one.\nLine two.\nLine three."
        chunks = chunker.chunk(text)

        assert len(chunks) >= 2
        # Verify all text is captured
        combined = "".join(c.text for c in chunks)
        assert "Line one" in combined
        assert "Line two" in combined

    def test_offset_calculation(self):
        """Test that offsets are correctly calculated."""
        chunker = LangChainTextChunker(chunk_size=20, chunk_overlap=10)
        text = "First part.\n\nSecond part."
        chunks = chunker.chunk(text)

        for chunk in chunks:
            # Verify offset points to correct position in original text
            assert text[chunk.start:chunk.end] == chunk.text

    def test_returns_textchunk_objects(self):
        """Test that chunk returns TextChunk objects."""
        chunker = LangChainTextChunker(chunk_size=50, chunk_overlap=10)
        chunks = chunker.chunk("Some text here")

        assert all(isinstance(c, TextChunk) for c in chunks)


class TestLangChainTextChunkerIntegration:
    """Integration tests for LangChainTextChunker."""

    def test_long_text_chunking(self):
        """Test chunking of longer text."""
        chunker = LangChainTextChunker(chunk_size=100, chunk_overlap=10)
        text = """This is a long document with multiple paragraphs.

Each paragraph contains some important information.

The chunker should split this text at paragraph boundaries first.

If paragraphs are too long, it falls back to line breaks.

Finally, it uses spaces as a last resort."""

        chunks = chunker.chunk(text)

        assert len(chunks) > 1
        # Verify all content is preserved
        all_text = " ".join(c.text for c in chunks)
        assert "long document" in all_text
        assert "paragraph boundaries" in all_text

    def test_uses_langchain_splitter(self):
        """Test that LangChain's splitter is actually being used."""
        chunker = LangChainTextChunker(chunk_size=50, chunk_overlap=10)
        # Verify the internal splitter exists
        assert hasattr(chunker, "_splitter")
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        assert isinstance(chunker._splitter, RecursiveCharacterTextSplitter)
