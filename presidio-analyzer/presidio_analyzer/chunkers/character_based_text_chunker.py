"""Character-based text chunker with word boundary preservation.

Based on gliner-spacy implementation:
https://github.com/theirstory/gliner-spacy/blob/main/gliner_spacy/pipeline.py#L60-L96
"""
from typing import List

from presidio_analyzer.chunkers.base_chunker import BaseTextChunker


class CharacterBasedTextChunker(BaseTextChunker):
    """Character-based text chunker with word boundary preservation."""

    def __init__(self, chunk_size: int, chunk_overlap: int = 0):
        """Initialize the local text chunker.
        
        :param chunk_size: Maximum characters per chunk (must be > 0)
        :param chunk_overlap: Characters to overlap between chunks (must be >= 0 and < chunk_size)
        """
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0")
        if chunk_overlap < 0 or chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be non-negative and less than chunk_size"
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, text: str) -> List[str]:
        """Split text into overlapping chunks at word boundaries.
        
        :param text: The input text to chunk
        :return: List of text chunks with overlap
        """
        if not text:
            return []

        chunks = []
        start = 0

        while start < len(text):
            # Calculate end position
            end = (
                start + self.chunk_size
                if start + self.chunk_size < len(text)
                else len(text)
            )

            # Extend to complete word boundary (space or newline)
            while end < len(text) and text[end] not in [" ", "\n"]:
                end += 1

            chunks.append(text[start:end])

            # Move start position with overlap (stop if we've covered all text)
            if end >= len(text):
                break
            start = end - self.chunk_overlap

        return chunks
