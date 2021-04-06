"""Deanonymize anonymized text by using deanonymize operators."""
import logging
from typing import List, Dict

from presidio_anonymizer.core.engine_base import EngineBase
from presidio_anonymizer.entities.engine import OperatorConfig
from presidio_anonymizer.entities.engine.anonymizer_result import AnonymizerResult
from presidio_anonymizer.entities.engine.result.engine_result import EngineResult
from presidio_anonymizer.operators import OperatorType


class DeanonymizeEngine(EngineBase):
    """Deanonymize text that was previously anonymized."""

    def __init__(self):
        self.logger = logging.getLogger("presidio-anonymizer")
        EngineBase.__init__(self)

    def deanonymize(self, text: str, entities: List[AnonymizerResult],
                    operators: Dict[str, OperatorConfig]) -> EngineResult:
        """
        Receive the text, entities and operators to perform deanonymization over.

        :param operators: the operators to apply on the anonymizer result entities
        :param text: the full text with the encrypted entities
        :param entities: list of encrypted entities
        :return: EngineResult - the new text and data about the deanonymized entities.
        """
        return self._operate(text,
                             entities,
                             operators,
                             OperatorType.Deanonymize)

    def get_deanonymizers(self) -> List[str]:
        """Return a list of supported deanonymizers."""
        names = [p for p in self.operators_factory.get_deanonymizers().keys()]
        return names
