"""Predefined recognizers package. Holds all the default recognizers."""

from .aba_routing_recognizer import AbaRoutingRecognizer
from .credit_card_recognizer import CreditCardRecognizer
from .crypto_recognizer import CryptoRecognizer
from .date_recognizer import DateRecognizer
from .domain_recognizer import DomainRecognizer
from .email_recognizer import EmailRecognizer
from .iban_recognizer import IbanRecognizer
from .ip_recognizer import IpRecognizer
from .medical_license_recognizer import MedicalLicenseRecognizer
from .sg_fin_recognizer import SgFinRecognizer
from .spacy_recognizer import SpacyRecognizer
from .stanza_recognizer import StanzaRecognizer
from .phone_recognizer import PhoneRecognizer
from .uk_nhs_recognizer import NhsRecognizer
from .us_bank_recognizer import UsBankRecognizer
from .us_driver_license_recognizer import UsLicenseRecognizer
from .us_itin_recognizer import UsItinRecognizer
from .us_passport_recognizer import UsPassportRecognizer
from .us_phone_recognizer import UsPhoneRecognizer
from .us_ssn_recognizer import UsSsnRecognizer
from .es_nif_recognizer import EsNifRecognizer

NLP_RECOGNIZERS = {"spacy": SpacyRecognizer, "stanza": StanzaRecognizer}

__all__ = [
    "AbaRoutingRecognizer",
    "CreditCardRecognizer",
    "CryptoRecognizer",
    "DateRecognizer",
    "DomainRecognizer",
    "EmailRecognizer",
    "IbanRecognizer",
    "IpRecognizer",
    "NhsRecognizer",
    "MedicalLicenseRecognizer",
    "SgFinRecognizer",
    "SpacyRecognizer",
    "StanzaRecognizer",
    "PhoneRecognizer",
    "UsBankRecognizer",
    "UsItinRecognizer",
    "UsLicenseRecognizer",
    "UsPassportRecognizer",
    "UsPhoneRecognizer",
    "UsSsnRecognizer",
    "EsNifRecognizer",
    "SpacyRecognizer",
    "StanzaRecognizer",
    "NLP_RECOGNIZERS",
]
