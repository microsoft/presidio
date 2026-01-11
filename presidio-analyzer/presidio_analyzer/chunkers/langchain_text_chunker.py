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

    def __init__(self, chunk_size: int = 250, chunk_overlap: int = 0):
        """Initialize the chunker.

        :param chunk_size: Maximum characters per chunk
        :param chunk_overlap: Characters to overlap between chunks
        """
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

        # Calculate offsets (LangChain doesn't provide them)
        chunks = []
        search_start = 0
        for chunk_text in chunks_text:
            offset = text.find(chunk_text, search_start)
            if offset == -1:
                offset = search_start
            chunks.append(TextChunk(
                text=chunk_text,
                start=offset,
                end=offset + len(chunk_text),
            ))
            search_start = offset + len(chunk_text) - self._chunk_overlap

        return chunks
