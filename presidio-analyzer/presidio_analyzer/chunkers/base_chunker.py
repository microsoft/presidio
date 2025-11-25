"""Abstract base class for text chunking strategies."""
from abc import ABC, abstractmethod
from typing import List


class BaseTextChunker(ABC):
    """Abstract base class for text chunking strategies."""

    @abstractmethod
    def chunk(self, text: str) -> List[str]:
        """Split text into chunks.
        
        :param text: The input text to split
        :return: List of text chunks
        """
        pass
