"""Text chunking strategies for handling long texts."""

from presidio_analyzer.chunkers.base_chunker import BaseTextChunker, TextChunk
from presidio_analyzer.chunkers.character_based_text_chunker import (
    CharacterBasedTextChunker,
)

_CHUNKER_REGISTRY = {
    "character": CharacterBasedTextChunker,
}


def create_chunker(kind: str, **kwargs) -> BaseTextChunker:
    """Factory helper for chunker selection by name.

    Kept minimal to avoid over-abstraction while letting configs select a chunker.
    """

    try:
        cls = _CHUNKER_REGISTRY[kind]
    except KeyError as exc:  # pragma: no cover - defensive for config typos
        raise ValueError(f"Unsupported chunker kind: {kind}") from exc
    return cls(**kwargs)


__all__ = [
    "BaseTextChunker",
    "TextChunk",
    "CharacterBasedTextChunker",
    "create_chunker",
]
