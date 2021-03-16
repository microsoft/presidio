import json
from typing import List

from presidio_anonymizer.entities.engine.engine_result_item import EngineResultItem


class EngineResult:
    def __init__(self, text: str, items: List[EngineResultItem] = None):
        self.text = text
        if not items:
            items = []
        self.items = items

    def append_item(self, entity: EngineResultItem):
        self.items.append(entity)

    def to_json(self) -> str:
        """Return a json string serializing this instance."""
        return json.dumps(self, default=lambda x: x.__dict__)

    def __eq__(self, other: 'EngineResult') -> bool:
        return self.text == other.text and all(
            map(lambda x, y: x == y, self.items, other.items)
        )