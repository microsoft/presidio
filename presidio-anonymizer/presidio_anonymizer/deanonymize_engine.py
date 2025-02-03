"""Deanonymize anonymized text by using deanonymize operators."""

import logging
from typing import Dict, List, Type

from presidio_anonymizer.core.engine_base import EngineBase
from presidio_anonymizer.entities import EngineResult, OperatorConfig, OperatorResult
from presidio_anonymizer.operators import Operator, OperatorType

logger = logging.getLogger("presidio-anonymizer")


class DeanonymizeEngine(EngineBase):
    """Deanonymize text that was previously anonymized."""

    def deanonymize(
        self,
        text: str,
        entities: List[OperatorResult],
        operators: Dict[str, OperatorConfig],
    ) -> EngineResult:
        """
        Receive the text, entities and operators to perform deanonymization over.

        :param operators: the operators to apply on the anonymizer result entities
        :param text: the full text with the encrypted entities
        :param entities: list of encrypted entities
        :return: EngineResult - the new text and data about the deanonymized entities.
        """
        return self._operate(text, entities, operators, OperatorType.Deanonymize)

    def get_deanonymizers(self) -> List[str]:
        """Return a list of supported deanonymizers."""
        names = [p for p in self.operators_factory.get_deanonymizers().keys()]
        return names

    def add_deanonymizer(self, deanonymizer_cls: Type[Operator]) -> None:
        """
        Add a new deanonymizer to the engine.

        anonymizer_cls: The deanonymizer class to add to the engine.
        """
        logger.info(f"Added deanonymizer {deanonymizer_cls.__name__}")
        self.operators_factory.add_deanonymize_operator(deanonymizer_cls)

    def remove_deanonymizer(self, deanonymizer_cls: Type[Operator]) -> None:
        """
        Remove a deanonymizer from the engine.

        deanonymizer_cls: The deanonymizer class to remove from the engine.
        """
        logger.info(f"Removed deanonymizer {deanonymizer_cls.__name__}")
        self.operators_factory.remove_deanonymize_operator(deanonymizer_cls)
