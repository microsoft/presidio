from presidio_anonymizer.operators import OperatorType
from presidio_anonymizer.operators.keep import BaseKeep


class DeanonymizeKeep(BaseKeep):
    """No-op deanonymizer that keeps the PII text unmodified.

    This is useful when you don't want to anonymize some types of PII,
    but wants to keep track of it with the other PIIs.
    """

    def operator_name(self) -> str:
        """Return operator name."""
        return "deanonymize_keep"

    def operator_type(self) -> OperatorType:
        """Return operator type."""
        return OperatorType.Deanonymize
