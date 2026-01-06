"""Abstract base class for text chunking strategies."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass
class TextChunk:
    """Represents a chunk of text with its position in the original text.
    
    :param text: The chunk content
    :param start: Start position in the original text (inclusive)
    :param end: End position in the original text (exclusive)
    """
    text: str
    start: int
    end: int


class BaseTextChunker(ABC):
    """Abstract base class for text chunking strategies.
    
    Subclasses must implement the chunk() method to split text into
    TextChunk objects that include both content and position information.
    """

    @abstractmethod
    def chunk(self, text: str) -> List[TextChunk]:
        """Split text into chunks with position information.

        :param text: The input text to split
        :return: List of TextChunk objects with text and position data
        """
        pass
