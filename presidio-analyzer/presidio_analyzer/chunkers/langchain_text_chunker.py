"""Text chunker using LangChain's RecursiveCharacterTextSplitter.

Requires: pip install langchain-text-splitters
"""

from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter

from presidio_analyzer.chunkers.base_chunker import BaseTextChunker, TextChunk


class LangChainTextChunker(BaseTextChunker):
    """Text chunker using LangChain's RecursiveCharacterTextSplitter.

    Uses separator hierarchy: paragraph → line → word → char.
    Requires: pip install langchain-text-splitters
    """

    def __init__(self, chunk_size: int = 250, chunk_overlap: int = 50):
        """Initialize the chunker.

        :param chunk_size: Maximum characters per chunk
        :param chunk_overlap: Characters to overlap between chunks
        """
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative")
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")

        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    @property
    def chunk_size(self) -> int:
        """Get the chunk size."""
        return self._chunk_size

    @property
    def chunk_overlap(self) -> int:
        """Get the chunk overlap."""
        return self._chunk_overlap

    def chunk(self, text: str) -> List[TextChunk]:
        """Split text into chunks with position information.

        :param text: The input text to chunk
        :return: List of TextChunk objects
        """
        if not text:
            return []

        chunks_text = self._splitter.split_text(text)

        # Calculate offsets deterministically using a running cursor to avoid
        # ambiguous find() matches when chunks repeat.
        chunks = []
        cursor = 0
        for chunk_text in chunks_text:
            # Ensure the chunk_text actually appears at or after the cursor.
            offset = text.find(chunk_text, cursor)
            if offset == -1:
                raise ValueError("Chunk text not found in source; chunking misalignment detected")
            if offset < cursor:
                raise ValueError("Chunk offsets would go backwards; chunking misalignment detected")

            chunks.append(TextChunk(
                text=chunk_text,
                start=offset,
                end=offset + len(chunk_text),
            ))

            # Advance cursor accounting for configured overlap
            cursor = offset + len(chunk_text) - self._chunk_overlap
            if cursor < offset:
                cursor = offset

        return chunks
