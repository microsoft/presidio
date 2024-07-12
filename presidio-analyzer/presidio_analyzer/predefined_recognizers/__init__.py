"""Predefined recognizers package. Holds all the default recognizers."""

from presidio_analyzer.predefined_recognizers.transformers_recognizer import (
    TransformersRecognizer,
)

from .at_passport_number import ATPassportNumber
from .aba_routing_recognizer import AbaRoutingRecognizer
from .au_abn_recognizer import AuAbnRecognizer
from .au_acn_recognizer import AuAcnRecognizer
from .au_bank_account_number import AUBankAccountNumber
from .au_medicare_recognizer import AuMedicareRecognizer
from .au_tfn_recognizer import AuTfnRecognizer
from .azure_ai_language import AzureAILanguageRecognizer
from .be_passport_number import BEPassportNumber
from .bu_passport_number import BUPassportNumber
from .cr_passport_number import CRPassportNumber
from .credit_card_recognizer import CreditCardRecognizer
from .crypto_recognizer import CryptoRecognizer
from .cy_passport_number import CYPassportNumber
from .cz_passport_number import CZPassportNumber
from .date_recognizer import DateRecognizer
from .de_passport_number import DEPassportNumber
from .dea_number import DrugEnforcementAgencyNumber
from .dk_passport_number import DKPassportNumber
from .ee_passport_number import EEPassportNumber
from .email_recognizer import EmailRecognizer
from .es_nie_recognizer import EsNieRecognizer
from .es_nif_recognizer import EsNifRecognizer
from .es_passport_number import ESPassportNumber
from .eu_gps_coordinates import EUGPSCoordinates
from .fi_passport_number import FIPassportNumber
from .fi_personal_identity_code_recognizer import FiPersonalIdentityCodeRecognizer
from .fr_passport_number import FRPassportNumber
from .gr_passport_number import GRPassportNumber
from .hk_identity_number import HKIdentityCardNumber
from .hu_passport_number import HUPassportNumber
from .hu_personal_identification_number import HUPersonalIdentificationNumber
from .iban_recognizer import IbanRecognizer
from .ie_passport_number import IEPassportNumber
from .in_aadhaar_recognizer import InAadhaarRecognizer
from .in_pan_recognizer import InPanRecognizer
from .in_passport_recognizer import InPassportRecognizer
from .in_vehicle_registration_recognizer import InVehicleRegistrationRecognizer
from .in_voter_recognizer import InVoterRecognizer
from .ip_recognizer import IpRecognizer
from .it_driver_license_recognizer import ItDriverLicenseRecognizer
from .it_fiscal_code_recognizer import ItFiscalCodeRecognizer
from .it_identity_card_recognizer import ItIdentityCardRecognizer
from .it_passport_number import ITPassportNumber
from .it_passport_recognizer import ItPassportRecognizer
from .it_vat_code import ItVatCodeRecognizer
from .lt_passport_number import LTPassportNumber
from .lv_passport_number import LVPassportNumber
from .medical_license_recognizer import MedicalLicenseRecognizer
from .mt_passport_number import MTPassportNumber
from .nz_bank_account_number import NZBankAccountNumber
from .nz_drivers_license import NZDriversLicenseNumber
from .nz_inland_revenue_number import NZInlandRevenueNumber
from .nz_ministry_health_number import NZMinistryOfHealthNumber
from .nz_social_welfare_number import NZSocialWelfareNumber
from .phone_recognizer import PhoneRecognizer
from .pl_passport_number import PLPassportNumber
from .pl_pesel_recognizer import PlPeselRecognizer
from .pt_passport_number import PTPassportNumber
from .ro_passport_number import ROPassportNumber
from .se_passport_number import SEPassportNumber
from .sg_fin_recognizer import SgFinRecognizer
from .sg_uen_recognizer import SgUenRecognizer
from .sk_passport_number import SKPassportNumber
from .sl_passport_number import SLPassportNumber
from .spacy_recognizer import SpacyRecognizer
from .stanza_recognizer import StanzaRecognizer
from .swift_code import SWIFTCode
from .uk_nhs_recognizer import NhsRecognizer
from .uk_passport_number import UKPassportNumber
from .url_recognizer import UrlRecognizer
from .us_bank_recognizer import UsBankRecognizer
from .us_driver_license_recognizer import UsLicenseRecognizer
from .us_itin_recognizer import UsItinRecognizer

from .us_passport_recognizer import UsPassportRecognizer
from .us_ssn_recognizer import UsSsnRecognizer

from .amazon_s3_secret_key_recognizer import AmazonS3Key

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
    "PlPeselRecognizer",
    "AzureAILanguageRecognizer",
    "InAadhaarRecognizer",
    "InVehicleRegistrationRecognizer",
    "SgUenRecognizer",
    "InVoterRecognizer",
    "InPassportRecognizer",
    "FiPersonalIdentityCodeRecognizer",
    "EsNieRecognizer",

    "ATPassportNumber",
    "AUBankAccountNumber",
    "BEPassportNumber",
    "BUPassportNumber",
    "CRPassportNumber",
    "CYPassportNumber",
    "CZPassportNumber",
    "DEPassportNumber",
    "DrugEnforcementAgencyNumber",
    "DKPassportNumber",
    "EEPassportNumber",
    "ESPassportNumber",
    "EUGPSCoordinates",
    "FIPassportNumber",
    "FRPassportNumber",
    "GRPassportNumber",
    "HKIdentityCardNumber",
    "HUPassportNumber",
    "HUPersonalIdentificationNumber",
    "IEPassportNumber",
    "ITPassportNumber",
    "LTPassportNumber",
    "LVPassportNumber",
    "MTPassportNumber",
    "NZBankAccountNumber",
    "NZDriversLicenseNumber",
    "NZInlandRevenueNumber",
    "NZMinistryOfHealthNumber",
    "NZSocialWelfareNumber",
    "PLPassportNumber",
    "PTPassportNumber",
    "ROPassportNumber",
    "SEPassportNumber",
    "SKPassportNumber",
    "SLPassportNumber",
    "SWIFTCode",
    "UKPassportNumber",

    "AmazonS3Key",
]
