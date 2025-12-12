"""Tests for chunking utility functions."""
import pytest

from presidio_analyzer.chunkers import (
    CharacterBasedTextChunker,
    process_text_in_chunks,
    deduplicate_overlapping_entities,
)


class TestProcessTextInChunks:
    """Test process_text_in_chunks utility function."""

    def test_short_text_no_chunking(self):
        """Test text shorter than chunk size is not chunked."""
        chunker = CharacterBasedTextChunker(chunk_size=100, chunk_overlap=20)
        text = "Short text"
        predict_func = lambda chunk: [{"start": 0, "end": 5, "label": "PERSON", "score": 0.9}]
        
        result = process_text_in_chunks(text, chunker, predict_func)
        
        assert len(result) == 1
        assert result[0]["start"] == 0
        assert result[0]["end"] == 5

    def test_long_text_with_offset_adjustment(self):
        """Test offset adjustment for chunked text."""
        chunker = CharacterBasedTextChunker(chunk_size=20, chunk_overlap=5)
        text = "John Smith lives in New York City with Jane Doe"
        
        # Mock predict function that finds entities in each chunk
        def predict_func(chunk):
            if "John" in chunk:
                return [{"start": 0, "end": 10, "label": "PERSON", "score": 0.9}]
            elif "Jane" in chunk:
                idx = chunk.index("Jane")
                return [{"start": idx, "end": idx + 8, "label": "PERSON", "score": 0.85}]
            return []
        
        result = process_text_in_chunks(text, chunker, predict_func)
        
        # First entity should be at original position
        assert result[0]["start"] == 0
        assert result[0]["end"] == 10
        # Second entity should have adjusted offset
        assert result[1]["start"] > 20  # In second chunk

    def test_empty_predictions(self):
        """Test handling of no predictions."""
        chunker = CharacterBasedTextChunker(chunk_size=50, chunk_overlap=10)
        text = "Some text without entities"
        predict_func = lambda chunk: []
        
        result = process_text_in_chunks(text, chunker, predict_func)
        
        assert result == []


class TestDeduplicateOverlappingEntities:
    """Test deduplicate_overlapping_entities utility function."""

    def test_no_duplicates(self):
        """Test predictions with no overlap."""
        predictions = [
            {"start": 0, "end": 10, "label": "PERSON", "score": 0.9},
            {"start": 20, "end": 30, "label": "PERSON", "score": 0.85},
        ]
        
        result = deduplicate_overlapping_entities(predictions)
        
        assert len(result) == 2
        assert result[0]["start"] == 0
        assert result[1]["start"] == 20

    def test_exact_duplicates_keeps_highest_score(self):
        """Test exact duplicates keeps highest scoring entity."""
        predictions = [
            {"start": 0, "end": 10, "label": "PERSON", "score": 0.9},
            {"start": 0, "end": 10, "label": "PERSON", "score": 0.85},
        ]
        
        result = deduplicate_overlapping_entities(predictions)
        
        assert len(result) == 1
        assert result[0]["score"] == 0.9

    def test_overlapping_duplicates(self):
        """Test overlapping entities are deduplicated."""
        predictions = [
            {"start": 0, "end": 10, "label": "PERSON", "score": 0.9},
            {"start": 3, "end": 13, "label": "PERSON", "score": 0.85},
        ]
        
        result = deduplicate_overlapping_entities(predictions)
        
        # Overlap is 7 chars, ratio = 0.7 > 0.5 threshold
        assert len(result) == 1
        assert result[0]["score"] == 0.9

    def test_different_labels_not_deduplicated(self):
        """Test overlapping entities with different labels are kept."""
        predictions = [
            {"start": 0, "end": 10, "label": "PERSON", "score": 0.9},
            {"start": 5, "end": 15, "label": "LOCATION", "score": 0.85},
        ]
        
        result = deduplicate_overlapping_entities(predictions)
        
        assert len(result) == 2

    def test_low_overlap_not_deduplicated(self):
        """Test entities with low overlap are not deduplicated."""
        predictions = [
            {"start": 0, "end": 10, "label": "PERSON", "score": 0.9},
            {"start": 9, "end": 20, "label": "PERSON", "score": 0.85},
        ]
        
        result = deduplicate_overlapping_entities(predictions, overlap_threshold=0.6)
        
        # Overlap is only 1 char out of 10, ratio = 0.1, below threshold
        assert len(result) == 2

    def test_empty_predictions(self):
        """Test empty predictions list."""
        result = deduplicate_overlapping_entities([])
        assert result == []

    def test_sorted_by_position(self):
        """Test results are sorted by start position."""
        predictions = [
            {"start": 20, "end": 30, "label": "PERSON", "score": 0.9},
            {"start": 0, "end": 10, "label": "PERSON", "score": 0.85},
            {"start": 40, "end": 50, "label": "PERSON", "score": 0.95},
        ]
        
        result = deduplicate_overlapping_entities(predictions)
        
        assert result[0]["start"] == 0
        assert result[1]["start"] == 20
        assert result[2]["start"] == 40

    def test_custom_overlap_threshold(self):
        """Test custom overlap threshold."""
        predictions = [
            {"start": 0, "end": 10, "label": "PERSON", "score": 0.9},
            {"start": 5, "end": 15, "label": "PERSON", "score": 0.85},
        ]
        
        # With 0.3 threshold, should deduplicate (overlap ratio = 0.5)
        result = deduplicate_overlapping_entities(predictions, overlap_threshold=0.3)
        assert len(result) == 1
        
        # With 0.7 threshold, should keep both (overlap ratio = 0.5 < 0.7)
        result = deduplicate_overlapping_entities(predictions, overlap_threshold=0.7)
        assert len(result) == 2
