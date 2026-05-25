"""Tests for TokenizerBasedTextChunker."""
from unittest.mock import MagicMock

import pytest

from presidio_analyzer.chunkers.tokenizer_based_text_chunker import (
    TokenizerBasedTextChunker,
)


def _make_tokenizer(tokens: list, offsets: list, model_max_length: int = 512):
    """Build a minimal mock tokenizer that returns fixed token/offset data."""
    tokenizer = MagicMock()
    tokenizer.model_max_length = model_max_length
    tokenizer.return_value = {
        "input_ids": tokens,
        "offset_mapping": offsets,
    }
    return tokenizer


def test_short_text_returns_single_chunk():
    """Text shorter than max_tokens produces exactly one chunk covering full text."""
    text = "Hello world"
    # 2 tokens, well within max_tokens=512
    tokens = [1, 2]
    offsets = [(0, 5), (6, 11)]
    tokenizer = _make_tokenizer(tokens, offsets)

    chunker = TokenizerBasedTextChunker(tokenizer=tokenizer, max_tokens=512)
    chunks = chunker.chunk(text)

    assert len(chunks) == 1
    assert chunks[0].start == 0
    assert chunks[0].end == len(text)
    assert chunks[0].text == text


def test_empty_text_returns_no_chunks():
    tokenizer = _make_tokenizer([], [])
    chunker = TokenizerBasedTextChunker(tokenizer=tokenizer, max_tokens=10, overlap_tokens=2)
    assert chunker.chunk("") == []


def test_long_text_splits_into_multiple_chunks():
    """Text with more tokens than max_tokens is split into overlapping chunks."""
    # 10 tokens, each occupying 2 chars: "aa bb cc dd ee ff gg hh ii jj"
    text = "aa bb cc dd ee ff gg hh ii jj"
    offsets = [
        (0, 2), (3, 5), (6, 8), (9, 11), (12, 14),
        (15, 17), (18, 20), (21, 23), (24, 26), (27, 29),
    ]
    tokens = list(range(10))
    tokenizer = _make_tokenizer(tokens, offsets)

    chunker = TokenizerBasedTextChunker(tokenizer=tokenizer, max_tokens=4, overlap_tokens=1)
    chunks = chunker.chunk(text)

    # step = 4 - 1 = 3 tokens per advance
    # chunk 0: tokens 0-3  -> chars 0..11
    # chunk 1: tokens 3-6  -> chars 9..20
    # chunk 2: tokens 6-9  -> chars 18..29
    assert len(chunks) == 3
    assert chunks[0].start == 0
    assert chunks[0].end == offsets[3][1]
    assert chunks[1].start == offsets[3][0]
    assert chunks[2].end == offsets[9][1]


def test_chunks_have_correct_text_content():
    text = "hello world foo"
    offsets = [(0, 5), (6, 11), (12, 15)]
    tokens = [1, 2, 3]
    tokenizer = _make_tokenizer(tokens, offsets)

    chunker = TokenizerBasedTextChunker(tokenizer=tokenizer, max_tokens=2, overlap_tokens=0)
    chunks = chunker.chunk(text)

    assert chunks[0].text == text[chunks[0].start:chunks[0].end]
    assert chunks[1].text == text[chunks[1].start:chunks[1].end]


def test_default_max_tokens_fallback_for_absurd_value():
    """Tokenizers with unrealistic model_max_length fall back to 512."""
    tokenizer = _make_tokenizer([], [], model_max_length=int(1e30))
    chunker = TokenizerBasedTextChunker(tokenizer=tokenizer)
    assert chunker.max_tokens == 512


def test_default_max_tokens_uses_model_max_length():
    """Tokenizers with reasonable model_max_length are respected."""
    tokenizer = _make_tokenizer([], [], model_max_length=1024)
    chunker = TokenizerBasedTextChunker(tokenizer=tokenizer)
    assert chunker.max_tokens == 1024


def test_default_max_tokens_uses_small_model_max_length():
    tokenizer = _make_tokenizer([], [], model_max_length=128)
    chunker = TokenizerBasedTextChunker(tokenizer=tokenizer, overlap_tokens=10)
    assert chunker.max_tokens == 128


def test_invalid_max_tokens_raises():
    tokenizer = _make_tokenizer([], [])
    with pytest.raises(ValueError, match="max_tokens must be greater than 0"):
        TokenizerBasedTextChunker(tokenizer=tokenizer, max_tokens=0)


def test_invalid_overlap_raises():
    tokenizer = _make_tokenizer([], [])
    with pytest.raises(ValueError, match="overlap_tokens"):
        TokenizerBasedTextChunker(tokenizer=tokenizer, max_tokens=10, overlap_tokens=10)
