"""Predefined recognizers package. Holds all the default recognizers."""

from presidio_analyzer.predefined_recognizers.transformers_recognizer import (
    TransformersRecognizer,
)

from .aba_routing_recognizer import AbaRoutingRecognizer
from .au_abn_recognizer import AuAbnRecognizer
from .au_acn_recognizer import AuAcnRecognizer
from .au_medicare_recognizer import AuMedicareRecognizer
from .au_tfn_recognizer import AuTfnRecognizer
from .azure_ai_language import AzureAILanguageRecognizer
from .credit_card_recognizer import CreditCardRecognizer
from .crypto_recognizer import CryptoRecognizer
from .date_recognizer import DateRecognizer
from .email_recognizer import EmailRecognizer
from .es_nie_recognizer import EsNieRecognizer
from .es_nif_recognizer import EsNifRecognizer
from .fi_personal_identity_code_recognizer import FiPersonalIdentityCodeRecognizer
from .gliner_recognizer import GLiNERRecognizer
from .iban_recognizer import IbanRecognizer
from .in_aadhaar_recognizer import InAadhaarRecognizer
from .in_pan_recognizer import InPanRecognizer
from .in_passport_recognizer import InPassportRecognizer
from .in_vehicle_registration_recognizer import InVehicleRegistrationRecognizer
from .in_voter_recognizer import InVoterRecognizer
from .ip_recognizer import IpRecognizer
from .it_driver_license_recognizer import ItDriverLicenseRecognizer
from .it_fiscal_code_recognizer import ItFiscalCodeRecognizer
from .it_identity_card_recognizer import ItIdentityCardRecognizer
from .it_passport_recognizer import ItPassportRecognizer
from .it_vat_code import ItVatCodeRecognizer
from .medical_license_recognizer import MedicalLicenseRecognizer
from .phone_recognizer import PhoneRecognizer
from .pl_pesel_recognizer import PlPeselRecognizer
from .sg_fin_recognizer import SgFinRecognizer
from .sg_uen_recognizer import SgUenRecognizer
from .spacy_recognizer import SpacyRecognizer
from .stanza_recognizer import StanzaRecognizer
from .uk_nhs_recognizer import NhsRecognizer
from .uk_nino_recognizer import UkNinoRecognizer
from .url_recognizer import UrlRecognizer
from .us_bank_recognizer import UsBankRecognizer
from .us_driver_license_recognizer import UsLicenseRecognizer
from .us_itin_recognizer import UsItinRecognizer
from .us_passport_recognizer import UsPassportRecognizer
from .us_ssn_recognizer import UsSsnRecognizer

PREDEFINED_RECOGNIZERS = [
    "PhoneRecognizer",
    "CreditCardRecognizer",
    "CryptoRecognizer",
    "DateRecognizer",
    "EmailRecognizer",
    "IpRecognizer",
    "IbanRecognizer",
    "MedicalLicenseRecognizer",
    "UrlRecognizer",
]

NLP_RECOGNIZERS = {
    "spacy": SpacyRecognizer,
    "stanza": StanzaRecognizer,
    "transformers": TransformersRecognizer,
}

__all__ = [
    "AbaRoutingRecognizer",
    "CreditCardRecognizer",
    "CryptoRecognizer",
    "DateRecognizer",
    "EmailRecognizer",
    "IbanRecognizer",
    "IpRecognizer",
    "NhsRecognizer",
    "MedicalLicenseRecognizer",
    "PhoneRecognizer",
    "SgFinRecognizer",
    "UrlRecognizer",
    "UsBankRecognizer",
    "UsItinRecognizer",
    "UsLicenseRecognizer",
    "UsPassportRecognizer",
    "UsSsnRecognizer",
    "EsNifRecognizer",
    "SpacyRecognizer",
    "StanzaRecognizer",
    "NLP_RECOGNIZERS",
    "AuAbnRecognizer",
    "AuAcnRecognizer",
    "AuTfnRecognizer",
    "AuMedicareRecognizer",
    "TransformersRecognizer",
    "ItDriverLicenseRecognizer",
    "ItFiscalCodeRecognizer",
    "ItVatCodeRecognizer",
    "ItIdentityCardRecognizer",
    "ItPassportRecognizer",
    "InPanRecognizer",
    "GLiNERRecognizer",
    "PlPeselRecognizer",
    "AzureAILanguageRecognizer",
    "InAadhaarRecognizer",
    "InVehicleRegistrationRecognizer",
    "SgUenRecognizer",
    "InVoterRecognizer",
    "InPassportRecognizer",
    "FiPersonalIdentityCodeRecognizer",
    "EsNieRecognizer",
    "UkNinoRecognizer",
]
