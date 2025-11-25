"""Tests for text chunking strategies."""
import pytest

from presidio_analyzer.chunkers import LocalTextChunker


class TestLocalTextChunker:
    """Test LocalTextChunker implementation."""

    def test_empty_text(self):
        """Test chunking empty text."""
        chunker = LocalTextChunker(chunk_size=100, chunk_overlap=20)
        result = chunker.chunk("")
        assert result == []

    def test_short_text(self):
        """Test text shorter than chunk_size."""
        chunker = LocalTextChunker(chunk_size=100, chunk_overlap=20)
        text = "This is a short text."
        result = chunker.chunk(text)
        assert len(result) == 1
        assert result[0] == text

    def test_long_text_without_overlap(self):
        """Test long text with no overlap."""
        chunker = LocalTextChunker(chunk_size=3, chunk_overlap=0)
        text = "1 2 3 4"  # 7 chars
        result = chunker.chunk(text)
        # Actual behavior: word boundaries extend chunks: ["1 2", " 3 4"]
        assert len(result) == 2
        assert result[0] == "1 2"
        assert result[1] == " 3 4"

    def test_long_text_with_overlap(self):
        """Test long text with overlap."""
        chunker = LocalTextChunker(chunk_size=5, chunk_overlap=2)
        text = "1 3 5 7 9"  # 9 chars: positions 0-8
        result = chunker.chunk(text)
        
        assert len(result) == 2
        assert result[0] == "1 3 5"
        assert result[1] == " 5 7 9"
        # Verify overlap exists
        assert result[0].endswith(" 5") and result[1].startswith(" 5")

    def test_word_boundary_preservation(self):
        """Test that chunks extend to word boundaries."""
        chunker = LocalTextChunker(chunk_size=8, chunk_overlap=2)
        text = "one two three four"
        result = chunker.chunk(text)
        # Chunks extend to word boundaries: "one two three" (13 chars) instead of breaking at 8
        assert result[0] == "one two three"
        assert len(result) == 2

    def test_exact_chunk_size(self):
        """Test text that's exactly chunk_size."""
        chunker = LocalTextChunker(chunk_size=5, chunk_overlap=2)
        text = "1 2 3"
        result = chunker.chunk(text)
        assert len(result) == 1
        assert result[0] == text

    def test_validation_zero_chunk_size(self):
        """Test that chunk_size must be > 0."""
        with pytest.raises(ValueError, match="chunk_size must be greater than 0"):
            LocalTextChunker(chunk_size=0, chunk_overlap=5)

    def test_validation_negative_chunk_size(self):
        """Test that chunk_size cannot be negative."""
        with pytest.raises(ValueError, match="chunk_size must be greater than 0"):
            LocalTextChunker(chunk_size=-10, chunk_overlap=5)

    def test_validation_negative_overlap(self):
        """Test that overlap cannot be negative."""
        with pytest.raises(
            ValueError, match="chunk_overlap must be non-negative and less than chunk_size"
        ):
            LocalTextChunker(chunk_size=100, chunk_overlap=-5)

    def test_validation_overlap_equals_chunk_size(self):
        """Test that overlap cannot equal chunk_size."""
        with pytest.raises(
            ValueError, match="chunk_overlap must be non-negative and less than chunk_size"
        ):
            LocalTextChunker(chunk_size=100, chunk_overlap=100)

    def test_validation_overlap_greater_than_chunk_size(self):
        """Test that overlap cannot exceed chunk_size."""
        with pytest.raises(
            ValueError, match="chunk_overlap must be non-negative and less than chunk_size"
        ):
            LocalTextChunker(chunk_size=50, chunk_overlap=75)

    def test_multiple_chunks_coverage(self):
        """Test that chunks cover entire text."""
        chunker = LocalTextChunker(chunk_size=5, chunk_overlap=1)
        text = "1 2 3 4 5 6"  # 11 chars
        result = chunker.chunk(text)
        # Verify all numbers appear in at least one chunk
        all_text = "".join(result)
        assert all(num in all_text for num in ["1", "2", "3", "4", "5", "6"])

    def test_newline_handling(self):
        """Test that newlines are preserved and treated as word boundaries."""
        chunker = LocalTextChunker(chunk_size=10, chunk_overlap=0)
        text = "line1\nline2\nline3"
        result = chunker.chunk(text)
        # Newlines should be preserved in output
        combined = "".join(result)
        assert combined == text
        # Verify newlines exist in chunks
        assert any("\n" in chunk for chunk in result)

    def test_default_parameters(self):
        """Test chunker with default overlap (0)."""
        chunker = LocalTextChunker(chunk_size=5)  # No overlap specified
        text = "1 2 3 4"
        result = chunker.chunk(text)
        assert len(result) == 2

    def test_very_long_text(self):
        """Test chunking very long text."""
        chunker = LocalTextChunker(chunk_size=10, chunk_overlap=2)
        text = " ".join([str(i) for i in range(50)])  # "0 1 2 3..."
        result = chunker.chunk(text)
        # Should create many chunks
        assert len(result) > 5
        # Verify chunks are reasonable size
        for chunk in result:
            assert len(chunk) <= 15

    def test_real_world_example(self):
        """Test with real-world PII detection scenario."""
        chunker = LocalTextChunker(chunk_size=250, chunk_overlap=50)
        text = """John Smith's credit card number is 4532-1234-5678-9010. 
        His social security number is 123-45-6789 and his email is john.smith@example.com.
        He lives at 123 Main Street, Anytown, ST 12345. 
        For contact, his phone number is (555) 123-4567."""
        result = chunker.chunk(text)
        # Should be 1-2 chunks depending on exact length
        assert 1 <= len(result) <= 2
        # All PII should be present in at least one chunk
        all_text = " ".join(result)
        assert "4532-1234-5678-9010" in all_text
        assert "123-45-6789" in all_text
        assert "john.smith@example.com" in all_text
