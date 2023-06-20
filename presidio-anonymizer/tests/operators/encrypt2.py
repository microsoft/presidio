

from typing import Dict

from presidio_anonymizer.operators import Encrypt


class Encrypt2(Encrypt):

    def operate(self, text: str = None, params: Dict = None) -> str:
        encrypted_text = super().operate(text, params)
        return f"@@@{encrypted_text}@@@"

    def operator_name(self) -> str:
        """Return operator name."""
        return "encrypt2"