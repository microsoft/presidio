"""Handle a serializable anonymizer result."""
import json


class AnonymizerResult:
    """
    Anonymizer result.

    """

    def __init__(self, text=None, items=None):
        if items is None:
            items = []
        self.text = text
        self.items = items

    def set_text(self, text):
        self.text = text

    def add_item(self, item):
        self.items.append(item)

    def to_json(self) -> str:
        """Return a json string serializing this instance."""
        return json.dumps(self, default=lambda x: x.__dict__)

    def __eq__(self, other):
        """Verify two instances are equal."""

        return self.text == other.text and all(map(lambda x, y: x == y, self.items, other.items))