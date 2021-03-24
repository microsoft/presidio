"""Decrypt encrypted text by the 'encrypt' anonymizer."""
import logging
from typing import List, Dict

from presidio_anonymizer.operators import OperatorsFactory

from presidio_anonymizer.core.engine_base import EngineBase
from presidio_anonymizer.entities.engine import OperatorConfig, DeanonymizeConfig
from presidio_anonymizer.entities.engine.anonymizer_result import AnonymizerResult
from presidio_anonymizer.entities.engine.result.engine_result import EngineResult


class DeanonymizeEngine(EngineBase):
    """Decrypting text that was previously anonymized using a 'decrypt' anonymizer."""

    def __init__(self):
        self.logger = logging.getLogger("presidio-anonymizer")
        EngineBase.__init__(self)

    def deanonymize(self, text: str, entities: List[AnonymizerResult],
                    operators: Dict[str, DeanonymizeConfig]) -> EngineResult:
        """
        Receive the text and the entities and decrypt accordingly.

        :param operators: the operators to apply on the anonymizer result entities
        :param text: the full text with the encrypted entities
        :param entities: list of encrypted entities
        :return: EngineResult - the new text and data about the decrypted entities.
        """
        return self._operate(text,
                             entities,
                             operators)

    @staticmethod
    def get_deanonymizers() -> List[str]:
        """Return a list of supported deanonymizers."""
        names = [p for p in OperatorsFactory.get_deanonymizers().keys()]
        return names
