"""Handle a serializable decrypt request."""
from typing import List, Dict

from presidio_anonymizer.entities.decrypt.request import DecryptEntity

class DecryptRequest:
    """Decrypt request."""

    def __init__(self, text: str = None, items: List[DecryptEntity] = []):
        """Create AnonymizerResult entity.

        :param text: The anonymized text.
        :param items: List of PII entities and the indices
         of their replacements in the anonymized text.
        """
        self.text = text
        self.items = items

    def sorted_items(self, reverse: bool = False):
        return sorted(self.items, reverse=reverse)

    @classmethod
    def from_json(cls, json: Dict) -> 'AnonymizerResult':
        text = json.get("text")
        items = []
        decrypt_entity = json.get("items")
        if decrypt_entity:
            for result in decrypt_entity:
                items.append(DecryptEntity.from_json(result))
        return cls(text, items)
