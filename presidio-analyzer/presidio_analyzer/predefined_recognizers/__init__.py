"""Predefined recognizers package. Holds all the default recognizers."""

from presidio_analyzer.predefined_recognizers.transformers_recognizer import (
    TransformersRecognizer,
)

from .aba_routing_recognizer import AbaRoutingRecognizer
from .amazon_s3_secret_key_recognizer import AmazonS3KeyRecognizer
from .at_passport_recognizer import AtPassportRecognizer
from .au_abn_recognizer import AuAbnRecognizer
from .au_acn_recognizer import AuAcnRecognizer
from .au_bank_account_recognizer import AuBankAccountRecognizer
from .au_medicare_recognizer import AuMedicareRecognizer
from .au_tfn_recognizer import AuTfnRecognizer
from .azure_ai_language import AzureAILanguageRecognizer
from .be_passport_recognizer import BePassportRecognizer
from .bu_passport_recognizer import BuPassportRecognizer
from .cr_passport_recognizer import CrPassportRecognizer
from .credit_card_recognizer import CreditCardRecognizer
from .crypto_recognizer import CryptoRecognizer
from .cy_passport_recognizer import CyPassportRecognizer
from .cz_passport_recognizer import CzPassportRecognizer
from .date_recognizer import DateRecognizer
from .de_passport_recognizer import DePassportRecognizer
from .dea_number_recognizer import DrugEnforcementAgencyNumberRecognizer
from .dk_passport_recognizer import DkPassportRecognizer
from .ee_passport_recognizer import EePassportRecognizer
from .email_recognizer import EmailRecognizer
from .es_nie_recognizer import EsNieRecognizer
from .es_nif_recognizer import EsNifRecognizer
from .es_passport_number import EsPassportRecognizer
from .eu_gps_coordinates_recognizer import EUGPSCoordinatesRecognizer
from .fi_passport_recognizer import FiPassportRecognizer
from .fi_personal_identity_code_recognizer import FiPersonalIdentityCodeRecognizer
from .fr_passport_recognizer import FrPassportRecognizer
from .gr_passport_recognizer import GrPassportRecognizer
from .hk_identity_recognizer import HkIdentityCardRecognizer
from .hu_passport_recognizer import HuPassportRecognizer
from .hu_personal_id_recognizer import HuPersonalIdentificationRecognizer
from .iban_recognizer import IbanRecognizer
from .ie_passport_recognizer import IePassportRecognizer
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
from .lt_passport_recognizer import LtPassportRecognizer
from .lv_passport_recognizer import LvPassportRecognizer
from .medical_license_recognizer import MedicalLicenseRecognizer
from .mt_passport_recognizer import MtPassportRecognizer
from .nz_bank_account_recognizer import NzBankAccountRecognizer
from .nz_drivers_license_recognizer import NzDriversLicenseRecognizer
from .nz_inland_revenue_number_recognizer import NzInlandRevenueNumberRecognizer
from .nz_ministry_health_number_recognizer import NzMinistryOfHealthNumberRecognizer
from .nz_social_welfare_number_recognizer import NZSocialWelfareNumberRecognizer
from .phone_recognizer import PhoneRecognizer
from .pl_passport_recognizer import PlPassportRecognizer
from .pl_pesel_recognizer import PlPeselRecognizer
from .pt_passport_recognizer import PtPassportRecognizer
from .ro_passport_recognizer import RoPassportRecognizer
from .se_passport_recognizer import SePassportRecognizer
from .sg_fin_recognizer import SgFinRecognizer
from .sg_uen_recognizer import SgUenRecognizer
from .sk_passport_recognizer import SkPassportRecognizer
from .sl_passport_recognizer import SlPassportRecognizer
from .spacy_recognizer import SpacyRecognizer
from .stanza_recognizer import StanzaRecognizer
from .swift_code_recognizer import SWIFTCodeRecognizer
from .uk_nhs_recognizer import NhsRecognizer
from .uk_passport_recognizer import UkPassportRecognizer
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
    "PlPeselRecognizer",
    "AzureAILanguageRecognizer",
    "InAadhaarRecognizer",
    "InVehicleRegistrationRecognizer",
    "SgUenRecognizer",
    "InVoterRecognizer",
    "InPassportRecognizer",
    "FiPersonalIdentityCodeRecognizer",
    "EsNieRecognizer",

    "AtPassportRecognizer",
    "AuBankAccountRecognizer",
    "BePassportRecognizer",
    "BuPassportRecognizer",
    "CrPassportRecognizer",
    "CyPassportRecognizer",
    "CzPassportRecognizer",
    "DePassportRecognizer",
    "DrugEnforcementAgencyNumberRecognizer",
    "DkPassportRecognizer",
    "EePassportRecognizer",
    "EsPassportRecognizer",
    "EUGPSCoordinatesRecognizer",
    "FiPassportRecognizer",
    "FrPassportRecognizer",
    "GrPassportRecognizer",
    "HkIdentityCardRecognizer",
    "HuPassportRecognizer",
    "HuPersonalIdentificationRecognizer",
    "IePassportRecognizer",
    "ItPassportRecognizer",
    "LtPassportRecognizer",
    "LvPassportRecognizer",
    "MtPassportRecognizer",
    "NzBankAccountRecognizer",
    "NzDriversLicenseRecognizer",
    "NzInlandRevenueNumberRecognizer",
    "NzMinistryOfHealthNumberRecognizer",
    "NZSocialWelfareNumberRecognizer",
    "PlPassportRecognizer",
    "PtPassportRecognizer",
    "RoPassportRecognizer",
    "SePassportRecognizer",
    "SkPassportRecognizer",
    "SlPassportRecognizer",
    "SWIFTCodeRecognizer",
    "UkPassportRecognizer",

    "AmazonS3KeyRecognizer",
]
