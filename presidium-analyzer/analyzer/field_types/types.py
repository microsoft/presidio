from field_types.globally import credit_card, crypto, email, ip, iban, domain, ner
from field_types.us import bank as usbank
from field_types.us import driver_license as usdriver
from field_types.us import itin as usitin
from field_types.us import passport as uspassport
from field_types.us import phone as usphone
from field_types.us import ssn as usssn
import os
import sys

parentPath = os.path.abspath("..")
if parentPath not in sys.path:
    sys.path.insert(0, parentPath)

from analyzer import common_pb2

types_refs = {
    common_pb2.FieldTypesEnum.Name(common_pb2.CREDIT_CARD):
    credit_card.CreditCard(),
    common_pb2.FieldTypesEnum.Name(common_pb2.CRYPTO): crypto.Crypto(),
    common_pb2.FieldTypesEnum.Name(common_pb2.DATE_TIME): ner.Ner(),
    common_pb2.FieldTypesEnum.Name(common_pb2.DOMAIN_NAME): domain.Domain(),
    common_pb2.FieldTypesEnum.Name(common_pb2.EMAIL_ADDRESS): email.Email(),
    common_pb2.FieldTypesEnum.Name(common_pb2.IBAN_CODE): iban.Iban(),
    common_pb2.FieldTypesEnum.Name(common_pb2.IP_ADDRESS): ip.Ip(),
    common_pb2.FieldTypesEnum.Name(common_pb2.NRP): ner.Ner(),
    common_pb2.FieldTypesEnum.Name(common_pb2.LOCATION): ner.Ner(),
    common_pb2.FieldTypesEnum.Name(common_pb2.PERSON): ner.Ner(),
    common_pb2.FieldTypesEnum.Name(common_pb2.US_BANK_NUMBER): usbank.UsBank(),
    common_pb2.FieldTypesEnum.Name(common_pb2.US_DRIVER_LICENSE): usdriver.UsDriverLicense(),
    common_pb2.FieldTypesEnum.Name(common_pb2.US_ITIN): usitin.UsItin(),
    common_pb2.FieldTypesEnum.Name(common_pb2.US_PASSPORT): uspassport.UsPassport(),
    common_pb2.FieldTypesEnum.Name(common_pb2.PHONE_NUMBER): usphone.Phone(),
    common_pb2.FieldTypesEnum.Name(common_pb2.US_SSN): usssn.UsSsn(),
}
