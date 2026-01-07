"""Text chunking strategies for handling long texts."""

from presidio_analyzer.chunkers.base_chunker import BaseTextChunker, TextChunk
from presidio_analyzer.chunkers.character_based_text_chunker import (
    CharacterBasedTextChunker,
)
from presidio_analyzer.chunkers.chunking_utils import (
    deduplicate_overlapping_entities,
    predict_with_chunking,
    process_text_in_chunks,
)

__all__ = [
    "BaseTextChunker",
    "TextChunk",
    "CharacterBasedTextChunker",
    "predict_with_chunking",
    "process_text_in_chunks",
    "deduplicate_overlapping_entities",
]
