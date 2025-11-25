"""Text chunking strategies for handling long texts."""
from presidio_analyzer.chunkers.base_chunker import BaseTextChunker
from presidio_analyzer.chunkers.local_text_chunker import LocalTextChunker
from presidio_analyzer.chunkers.chunking_utils import (
    predict_with_chunking,
    process_text_in_chunks,
    deduplicate_overlapping_entities,
)

__all__ = [
    "BaseTextChunker",
    "LocalTextChunker",
    "predict_with_chunking",
    "process_text_in_chunks",
    "deduplicate_overlapping_entities",
]
