"""Handle a serializable anonymizer result."""
import json

from presidio_anonymizer.entities.anonymized_text_index_item \
    import AnonymizedTextIndexItem


class AnonymizerResult:
    """Anonymizer result."""

    def __init__(self, text: str = None, items: list[AnonymizedTextIndexItem] = None):
        """Create AnonymizerResult entity.

        :param text: The anonymized text.
        :param items: List of PII entities and their indexes in the anonymized text.
        """
        if items is None:
            items = []
        self.text = text
        self.items = items

    def set_text(self, text: str):
        """Set a text."""
        self.text = text

    def add_item(self, item: AnonymizedTextIndexItem):
        """Add an item.

        :param item: an item to add to the list.
        """
        self.items.append(item)

    def normalize_item_indexes(self):
        """Normalize the indexes to be index from start."""
        text_len = len(self.text)
        for result_item in self.items:
            result_item.start = text_len - result_item.end
            result_item.end = result_item.start + len(result_item.anonymized_text)

    def to_json(self) -> str:
        """Return a json string serializing this instance."""
        return json.dumps(self, default=lambda x: x.__dict__)

    def __eq__(self, other) -> bool:
        """Verify two instances are equal.

        :return true if the two instances are equal, false otherwise.
        """

        return self.text == other.text and all(
            map(lambda x, y: x == y, self.items, other.items))
