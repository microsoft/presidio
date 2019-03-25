from analyzer import Pattern
from analyzer import PatternRecognizer

# pylint: disable=line-too-long,abstract-method
# Weak pattern: all passport numbers are a weak match, e.g., 14019033
REGEX = r'\b[0-9]{8,17}\b'

CONTEXT = [
    "bank"
    # Task #603: Support keyphrases: change to "checking account"
    # as part of keyphrase change
    "checking",
    "account",
    "account#",
    "acct",
    "saving",
    "debit"
]


class UsBankRecognizer(PatternRecognizer):
    """
    Recognizes US bank number using regex
    """

    def __init__(self):
        patterns = [Pattern('Bank Account (weak)', REGEX, 0.05)]
        super().__init__(supported_entity="US_BANK_NUMBER",
                         patterns=patterns, context=CONTEXT)
