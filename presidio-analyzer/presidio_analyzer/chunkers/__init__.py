"""Text chunking strategies for handling long texts."""

from presidio_analyzer.chunkers.base_chunker import BaseTextChunker, TextChunk
from presidio_analyzer.chunkers.character_based_text_chunker import (
    CharacterBasedTextChunker,
)
from presidio_analyzer.chunkers.text_chunker_provider import TextChunkerProvider

__all__ = [
    "BaseTextChunker",
    "TextChunk",
    "CharacterBasedTextChunker",
    "TextChunkerProvider",
    "TokenizerBasedTextChunker",
]


def __getattr__(name: str):
    """Lazy import for TokenizerBasedTextChunker to avoid requiring transformers."""
    if name == "TokenizerBasedTextChunker":
        from presidio_analyzer.chunkers.tokenizer_based_text_chunker import (
            TokenizerBasedTextChunker,
        )

        return TokenizerBasedTextChunker
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

