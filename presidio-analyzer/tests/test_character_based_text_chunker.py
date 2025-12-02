"""Tests for text chunking strategies."""
import pytest

from presidio_analyzer.chunkers import CharacterBasedTextChunker


class TestCharacterBasedTextChunker:
    """Test CharacterBasedTextChunker implementation."""

    def test_empty_text(self):
        """Test chunking empty text."""
        chunker = CharacterBasedTextChunker(chunk_size=100, chunk_overlap=20)
        result = chunker.chunk("")
        assert result == []

    def test_short_text(self):
        """Test text shorter than chunk_size."""
        chunker = CharacterBasedTextChunker(chunk_size=100, chunk_overlap=20)
        text = "This is a short text."
        result = chunker.chunk(text)
        assert len(result) == 1
        assert result[0] == text

    def test_long_text_without_overlap(self):
        """Test long text with no overlap."""
        chunker = CharacterBasedTextChunker(chunk_size=3, chunk_overlap=0)
        text = "1 2 3 4"  # 7 chars
        result = chunker.chunk(text)
        # Actual behavior: word boundaries extend chunks: ["1 2", " 3 4"]
        assert len(result) == 2
        assert result[0] == "1 2"
        assert result[1] == " 3 4"

    def test_long_text_with_overlap(self):
        """Test long text with overlap."""
        chunker = CharacterBasedTextChunker(chunk_size=5, chunk_overlap=2)
        text = "1 3 5 7 9"  # 9 chars: positions 0-8
        result = chunker.chunk(text)
        
        assert len(result) == 2
        assert result[0] == "1 3 5"
        assert result[1] == " 5 7 9"
        # Verify overlap exists
        assert result[0].endswith(" 5") and result[1].startswith(" 5")

    def test_word_boundary_preservation(self):
        """Test that chunks extend to word boundaries."""
        chunker = CharacterBasedTextChunker(chunk_size=8, chunk_overlap=2)
        text = "one two three four"
        result = chunker.chunk(text)
        # Chunks extend to word boundaries: "one two three" (13 chars) instead of breaking at 8
        assert result[0] == "one two three"
        assert len(result) == 2

    def test_exact_chunk_size(self):
        """Test text that's exactly chunk_size."""
        chunker = CharacterBasedTextChunker(chunk_size=5, chunk_overlap=2)
        text = "1 2 3"
        result = chunker.chunk(text)
        assert len(result) == 1
        assert result[0] == text

    def test_validation_zero_chunk_size(self):
        """Test that chunk_size must be > 0."""
        with pytest.raises(ValueError, match="chunk_size must be greater than 0"):
            CharacterBasedTextChunker(chunk_size=0, chunk_overlap=5)

    def test_validation_negative_chunk_size(self):
        """Test that chunk_size cannot be negative."""
        with pytest.raises(ValueError, match="chunk_size must be greater than 0"):
            CharacterBasedTextChunker(chunk_size=-10, chunk_overlap=5)

    def test_validation_negative_overlap(self):
        """Test that overlap cannot be negative."""
        with pytest.raises(
            ValueError, match="chunk_overlap must be non-negative and less than chunk_size"
        ):
            CharacterBasedTextChunker(chunk_size=100, chunk_overlap=-5)

    def test_validation_overlap_equals_chunk_size(self):
        """Test that overlap cannot equal chunk_size."""
        with pytest.raises(
            ValueError, match="chunk_overlap must be non-negative and less than chunk_size"
        ):
            CharacterBasedTextChunker(chunk_size=100, chunk_overlap=100)

    def test_validation_overlap_greater_than_chunk_size(self):
        """Test that overlap cannot exceed chunk_size."""
        with pytest.raises(
            ValueError, match="chunk_overlap must be non-negative and less than chunk_size"
        ):
            CharacterBasedTextChunker(chunk_size=50, chunk_overlap=75)

    def test_multiple_chunks_coverage(self):
        """Test that chunks cover entire text."""
        chunker = CharacterBasedTextChunker(chunk_size=5, chunk_overlap=1)
        text = "1 2 3 4 5 6"  # 11 chars: positions 0-10
        result = chunker.chunk(text)
        # Actual result: ['1 2 3', '3 4 5', '5 6']
        assert len(result) == 3
        assert result[0] == "1 2 3"
        assert result[1] == "3 4 5"
        assert result[2] == "5 6"
        # Verify all digits appear (overlap causes duplication in joined string)
        all_text = "".join(result)
        for digit in ["1", "2", "3", "4", "5", "6"]:
            assert digit in all_text

    def test_newline_handling(self):
        """Test that newlines are preserved and treated as word boundaries."""
        chunker = CharacterBasedTextChunker(chunk_size=10, chunk_overlap=0)
        text = "line1\nline2\nline3"  # 17 chars
        result = chunker.chunk(text)
        # Chunk 1: "line1\nline2" (12 chars, extends to newline boundary at position 11)
        # Chunk 2: "\nline3" (remaining 6 chars)
        assert len(result) == 2
        assert result[0] == "line1\nline2"
        assert result[1] == "\nline3"
        # Verify complete text preserved
        assert "".join(result) == text

    def test_default_parameters(self):
        """Test chunker with default overlap (0)."""
        chunker = CharacterBasedTextChunker(chunk_size=5)  # No overlap specified (default=0)
        text = "1 2 3 4"  # 7 chars
        result = chunker.chunk(text)
        # Chunk 1: "1 2 3" (5 chars, extends to word boundary at position 4)
        # Chunk 2: starts at position 5: " 4" (remaining)
        assert len(result) == 2
        assert result[0] == "1 2 3"
        assert result[1] == " 4"

    def test_very_long_text(self):
        """Test chunking very long text."""
        chunker = CharacterBasedTextChunker(chunk_size=10, chunk_overlap=2)
        text = " ".join([str(i) for i in range(50)])  # "0 1 2 3..."
        # Text: "0 1 2 3 4 5 6 7 8 9 10 11..." = 138 chars
        result = chunker.chunk(text)
        # With chunk_size=10, overlap=2, word boundaries: creates 16 chunks
        assert len(result) == 16
        # First chunk
        assert result[0] == "0 1 2 3 4 5"
        # Last chunk
        assert result[-1] == "48 49"
        # Verify all numbers appear in chunks
        all_text = " ".join(result)
        for i in range(50):
            assert str(i) in all_text

    def test_real_world_example(self):
        """Test with real-world PII detection scenario."""
        chunker = CharacterBasedTextChunker(chunk_size=250, chunk_overlap=50)
        text = """John Smith's credit card number is 4532-1234-5678-9010. 
        His social security number is 123-45-6789 and his email is john.smith@example.com.
        He lives at 123 Main Street, Anytown, ST 12345. 
        For contact, his phone number is (555) 123-4567."""
        result = chunker.chunk(text)
        # Text is 251 chars, creates 2 chunks with overlap
        assert len(result) == 2
        # All PII should be present across chunks
        all_text = " ".join(result)
        assert "4532-1234-5678-9010" in all_text
        assert "123-45-6789" in all_text
        assert "john.smith@example.com" in all_text
        assert "123-4567" in all_text

    def test_cjk_text_without_spaces(self):
        """Test CJK text without spaces extends to end of text."""
        chunker = CharacterBasedTextChunker(chunk_size=5, chunk_overlap=1)
        text = "你好世界测试"  # 6 Chinese characters, no spaces
        result = chunker.chunk(text)
        # No spaces, so first chunk extends all the way to end
        # (word boundary extension continues until end of text)
        assert len(result) == 1
        assert result[0] == text

    def test_unicode_emoji_handling(self):
        """Test Unicode characters and emojis are handled correctly."""
        chunker = CharacterBasedTextChunker(chunk_size=10, chunk_overlap=2)
        text = "Hello 👋 World 🌍 Test"
        result = chunker.chunk(text)
        # Verify emojis are preserved in chunks
        all_text = "".join(result)
        assert "👋" in all_text
        assert "🌍" in all_text
        # Verify all words appear (overlap may cause partial duplication)
        assert "Hello" in all_text
        assert "World" in all_text  # May appear as 'Worldld' due to overlap
        assert "Test" in all_text
