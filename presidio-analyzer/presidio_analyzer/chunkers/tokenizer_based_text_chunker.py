"""Tokenizer-based text chunker using HuggingFace tokenizers."""

import logging
from typing import TYPE_CHECKING, List, Optional, Union

from presidio_analyzer.chunkers.base_chunker import BaseTextChunker, TextChunk

if TYPE_CHECKING:
    from transformers import PreTrainedTokenizerBase

logger = logging.getLogger("presidio-analyzer")

# Fallback when the tokenizer does not expose a finite model_max_length
_DEFAULT_MAX_TOKENS = 512


class TokenizerBasedTextChunker(BaseTextChunker):
    """Text chunker that splits text based on tokenizer token counts.

    Unlike character-based chunking, this respects the model's actual token
    limit and avoids splitting mid-subword. Chunks are defined by token
    boundaries and mapped back to character offsets.

    Can be configured from YAML via the ``text_chunker`` field::

        text_chunker:
          chunker_type: tokenizer
          tokenizer: bert-base-uncased
          max_tokens: 512
          overlap_tokens: 32

    :param tokenizer: A HuggingFace tokenizer name (str) or a loaded
        PreTrainedTokenizer instance.
    :param max_tokens: Maximum number of tokens per chunk. Defaults to the
        tokenizer's model_max_length (falls back to 512 if not set or
        unreasonably large).
    :param overlap_tokens: Number of tokens to overlap between consecutive
        chunks (must be >= 0 and < max_tokens). Defaults to 32.
    """

    def __init__(
        self,
        tokenizer: Union[str, "PreTrainedTokenizerBase"],
        max_tokens: Optional[int] = None,
        overlap_tokens: int = 32,
    ):
        if isinstance(tokenizer, str):
            try:
                from transformers import AutoTokenizer
            except ImportError as e:
                raise ImportError(
                    "transformers is required to load a tokenizer by name. "
                    "Install it with: pip install transformers"
                ) from e
            tokenizer = AutoTokenizer.from_pretrained(tokenizer)

        self.tokenizer = tokenizer

        if not getattr(tokenizer, "is_fast", True):
            raise ValueError(
                "TokenizerBasedTextChunker requires a fast tokenizer "
                "(one that supports return_offsets_mapping). "
                "Use AutoTokenizer.from_pretrained(name, use_fast=True)."
            )

        if max_tokens is None:
            raw = getattr(tokenizer, "model_max_length", _DEFAULT_MAX_TOKENS)
            # Some tokenizers report absurdly large values (e.g. 1e30)
            if raw is None or raw > 1_000_000:
                max_tokens = _DEFAULT_MAX_TOKENS
            else:
                max_tokens = raw

            # Reserve space for special tokens ([CLS], [SEP], etc.) that the
            # NER pipeline adds automatically, so chunks don't exceed the
            # model's actual input limit.
            num_special = getattr(
                tokenizer, "num_special_tokens_to_add", lambda pair=False: 0
            )(pair=False)
            max_tokens = max(1, max_tokens - num_special)

            # Clamp overlap if auto-derived max_tokens is smaller than default overlap
            if overlap_tokens >= max_tokens:
                overlap_tokens = max(0, max_tokens - 1)
                logger.warning(
                    "overlap_tokens clamped to %d (max_tokens=%d)",
                    overlap_tokens,
                    max_tokens,
                )

        if max_tokens <= 0:
            raise ValueError("max_tokens must be greater than 0")
        if overlap_tokens < 0 or overlap_tokens >= max_tokens:
            raise ValueError(
                "overlap_tokens must be non-negative and less than max_tokens"
            )

        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens

    def chunk(self, text: str) -> List[TextChunk]:
        """Split text into token-aligned chunks with character offset tracking.

        :param text: The input text to chunk.
        :return: List of TextChunk objects with text and position information.
        """
        if not text:
            return []

        encoding = self.tokenizer(
            text,
            return_offsets_mapping=True,
            add_special_tokens=False,
            truncation=False,
        )

        offsets = encoding["offset_mapping"]
        num_tokens = len(offsets)

        logger.debug(
            "Chunking text: length=%d chars, %d tokens, max_tokens=%d, overlap=%d",
            len(text),
            num_tokens,
            self.max_tokens,
            self.overlap_tokens,
        )

        if num_tokens <= self.max_tokens:
            return [TextChunk(text=text, start=0, end=len(text))]

        chunks = []
        step = self.max_tokens - self.overlap_tokens
        start_token = 0

        while start_token < num_tokens:
            end_token = min(start_token + self.max_tokens, num_tokens)

            char_start = offsets[start_token][0]
            char_end = offsets[end_token - 1][1]

            chunks.append(
                TextChunk(
                    text=text[char_start:char_end], start=char_start, end=char_end
                )
            )

            if end_token >= num_tokens:
                break
            start_token += step

        logger.debug("Created %d chunks from text", len(chunks))
        return chunks
