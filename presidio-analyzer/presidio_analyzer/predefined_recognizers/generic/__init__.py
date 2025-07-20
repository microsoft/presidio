"""Generic recognizers package."""

from .credit_card_recognizer import CreditCardRecognizer
from .crypto_recognizer import CryptoRecognizer
from .email_recognizer import EmailRecognizer
from .iban_recognizer import IbanRecognizer
from .ip_recognizer import IpRecognizer
from .phone_recognizer import PhoneRecognizer
from .url_recognizer import UrlRecognizer

__all__ = [
    "CreditCardRecognizer",
    "CryptoRecognizer",
    "EmailRecognizer",
    "IbanRecognizer",
    "IpRecognizer",
    "PhoneRecognizer",
    "UrlRecognizer",
]
