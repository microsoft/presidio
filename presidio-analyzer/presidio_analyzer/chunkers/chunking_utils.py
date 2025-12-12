"""Utility functions for processing text with chunking strategies."""
from typing import Any, Callable, Dict, List

from presidio_analyzer.chunkers.base_chunker import BaseTextChunker


def predict_with_chunking(
    text: str,
    predict_func: Callable[[str], List[Dict[str, Any]]],
    chunker: BaseTextChunker,
) -> List[Dict[str, Any]]:
    """Process text with automatic chunking for long texts.

    For short text (≤ chunker.chunk_size), calls predict_func directly.
    For long text, chunks it and merges predictions with deduplication.

    :param text: Input text to process
    :param predict_func: Function that takes text and returns predictions
    :param chunker: Text chunking strategy (contains chunk_size and chunk_overlap)
    :return: List of predictions with correct offsets
    """
    if len(text) <= chunker.chunk_size:
        return predict_func(text)

    predictions = process_text_in_chunks(
        text=text,
        chunker=chunker,
        process_func=predict_func,
    )
    return deduplicate_overlapping_entities(predictions)

def process_text_in_chunks(
    text: str,
    chunker: BaseTextChunker,
    process_func: Callable[[str], List[Dict[str, Any]]],
) -> List[Dict[str, Any]]:
    """Process text in chunks and adjust entity offsets.

    :param text: Input text to process
    :param chunker: Text chunking strategy
    :param process_func: Function that takes chunk text and returns predictions
    :return: List of predictions with adjusted offsets
    """
    chunks = chunker.chunk(text)
    all_predictions = []
    offset = 0

    for chunk in chunks:
        chunk_predictions = process_func(chunk)

        # Adjust offsets to match original text position
        for pred in chunk_predictions:
            pred["start"] += offset
            pred["end"] += offset

        all_predictions.extend(chunk_predictions)
        offset += len(chunk) - chunker.chunk_overlap

    return all_predictions

def deduplicate_overlapping_entities(
    predictions: List[Dict[str, Any]], overlap_threshold: float = 0.5
) -> List[Dict[str, Any]]:
    """Remove duplicate entities from overlapping chunks.

    :param predictions: List of predictions with 'start', 'end', 'label',
        'score'
    :param overlap_threshold: Overlap ratio threshold to consider duplicates
        (default: 0.5)
    :return: Deduplicated list of predictions sorted by position
    """
    if not predictions:
        return predictions

    # Sort by score descending to keep highest scoring entities
    sorted_preds = sorted(predictions, key=lambda p: p["score"], reverse=True)
    unique = []

    for pred in sorted_preds:
        is_duplicate = False
        for kept in unique:
            # Check if same entity type and overlapping positions
            if pred["label"] == kept["label"]:
                overlap_start = max(pred["start"], kept["start"])
                overlap_end = min(pred["end"], kept["end"])

                if overlap_start < overlap_end:
                    # Calculate overlap ratio
                    overlap_len = overlap_end - overlap_start
                    pred_len = pred["end"] - pred["start"]
                    kept_len = kept["end"] - kept["start"]

                    # Check if overlap exceeds threshold
                    if overlap_len / min(pred_len, kept_len) > overlap_threshold:
                        is_duplicate = True
                        break

        if not is_duplicate:
            unique.append(pred)

    # Sort by position for consistent output
    return sorted(unique, key=lambda p: p["start"])
