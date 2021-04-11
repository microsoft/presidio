"""Handle a serializable anonymizer result."""
import json
from typing import List

from presidio_anonymizer.entities.engine.result import \
    OperatorResult


class EngineResult:
    """Anonymizer result."""

    def __init__(self, text: str = None, items: List[OperatorResult] = None):
        """Create AnonymizerResult entity.

        :param text: The anonymized text.
        :param items: List of PII entities and the indices
         of their replacements in the anonymized text.
        """
        if items is None:
            items = []
        self.text = text
        self.items = items

    def set_text(self, text: str):
        """Set a text."""
        self.text = text

    def add_item(self, item: OperatorResult):
        """Add an item.

        :param item: an item to add to the list.
        """
        self.items.append(item)

    def normalize_item_indexes(self):
        """Normalize the indexes to be index from start."""
        text_len = len(self.text)
        for result_item in self.items:
            result_item.start = text_len - result_item.end
            result_item.end = result_item.start + len(result_item.text)

    def to_json(self) -> str:
        """Return a json string serializing this instance."""
        return json.dumps(self, default=lambda x: x.__dict__)

    def __eq__(self, other) -> bool:
        """Verify two instances are equal.

        :return true if the two instances are equal, false otherwise.
        """
        return self.text == other.text and all(
            map(lambda x, y: x == y, self.items, other.items)
        )
