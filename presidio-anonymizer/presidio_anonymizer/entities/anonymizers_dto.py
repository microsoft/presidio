"""Wrap the AnonymizerDTO dictionary."""
import logging

from presidio_anonymizer.entities.anonymizer_dto import AnonymizerDTO


class AnonymizersDTO(dict):
    """Wrap the AnonymizerDTO dictionary."""

    logger = logging.getLogger("presidio-anonymizer")

    def get_anonymizer(self, entity_type: str):
        """
        Get the right anonymizer from the list.

        When anonymizer does not exist, we fall back to default.
        :param entity_type: the type of the text we want to do anonymizer over
        :return: anonymizer
        """
        anonymizer = self.get(entity_type)
        if not anonymizer:
            anonymizer = self.get("DEFAULT")
            if not anonymizer:
                anonymizer = AnonymizerDTO("replace", {})
        return anonymizer
