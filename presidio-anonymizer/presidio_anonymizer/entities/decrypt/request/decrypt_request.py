"""Handle a serializable decrypt request."""
from typing import List, Dict

from presidio_anonymizer.entities.decrypt.request import DecryptEntity


class DecryptRequest:
    """Decrypt request."""

    def __init__(self, text: str = None,
                 items: List[DecryptEntity] = []) -> 'DecryptRequest':
        """
        Create DecryptRequest entity.

        :param text: The anonymized text.
        :param items: List of encrypted entities, their text position and encryption
        key.
        """
        self.text = text
        self.items = items

    def sorted_items(self, reverse: bool = False) -> List[DecryptEntity]:
        """
        Get sorted items by where text location start from.

        :param reverse: By default from start to end
        :return: list of sorted items by their text start position.
        """
        return sorted(self.items, reverse=reverse)

    @classmethod
    def from_json(cls, json: Dict) -> 'DecryptRequest':
        """
        Create DecryptRequest entity.

        :param json e.g.:
        {
            "text": text,
            "items": [{
                "start": 0,
                "end": len(text),
                "key": "1111111111111111",
            }],
        }
        :return: DecryptRequest
        """
        text = json.get("text")
        items = []
        decrypt_entity = json.get("items")
        if decrypt_entity:
            for result in decrypt_entity:
                items.append(DecryptEntity.from_json(result))
        return cls(text, items)
