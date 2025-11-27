"""Text chunking strategies for handling long texts."""
from presidio_analyzer.chunkers.base_chunker import BaseTextChunker
from presidio_analyzer.chunkers.character_based_text_chunker import CharacterBasedTextChunker
from presidio_analyzer.chunkers.chunking_utils import (
    predict_with_chunking,
    process_text_in_chunks,
    deduplicate_overlapping_entities,
)

__all__ = [
    "BaseTextChunker",
    "CharacterBasedTextChunker",
    "predict_with_chunking",
    "deduplicate_overlapping_entities",
]
