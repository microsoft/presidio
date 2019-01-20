from field_types.globally import credit_card, crypto, email, ip, iban, domain, ner  # noqa: E501
from field_types.us import bank as usbank
from field_types.us import driver_license as usdriver
from field_types.us import itin as usitin
from field_types.us import passport as uspassport
from field_types.us import phone as usphone
from field_types.us import ssn as usssn
from field_types.uk import nhs as uknhs

import os
import sys

parentPath = os.path.abspath("..")
if parentPath not in sys.path:
    sys.path.insert(0, parentPath)

from analyzer import common_pb2  # noqa: E402


class FieldFactory(object):
    def create(type):
        if type == common_pb2.FieldTypesEnum.Name(common_pb2.CREDIT_CARD):
            return credit_card.CreditCard()
        if type == common_pb2.FieldTypesEnum.Name(common_pb2.CRYPTO):
            return crypto.Crypto()
        if type == common_pb2.FieldTypesEnum.Name(common_pb2.DOMAIN_NAME):
            return domain.Domain()
        if type == common_pb2.FieldTypesEnum.Name(common_pb2.EMAIL_ADDRESS):
            return email.Email()
        if type == common_pb2.FieldTypesEnum.Name(common_pb2.IBAN_CODE):
            return iban.Iban()
        if type == common_pb2.FieldTypesEnum.Name(common_pb2.IP_ADDRESS):
            return ip.Ip()
        if type == common_pb2.FieldTypesEnum.Name(common_pb2.US_BANK_NUMBER):
            return usbank.UsBank()
        if type == common_pb2.FieldTypesEnum.Name(
                common_pb2.US_DRIVER_LICENSE):
            return usdriver.UsDriverLicense()
        if type == common_pb2.FieldTypesEnum.Name(common_pb2.US_ITIN):
            return usitin.UsItin()
        if type == common_pb2.FieldTypesEnum.Name(common_pb2.US_PASSPORT):
            return uspassport.UsPassport()
        if type == common_pb2.FieldTypesEnum.Name(common_pb2.PHONE_NUMBER):
            return usphone.Phone()
        if type == common_pb2.FieldTypesEnum.Name(common_pb2.US_SSN):
            return usssn.UsSsn()
        if type == common_pb2.FieldTypesEnum.Name(common_pb2.UK_NHS):
            return uknhs.UkNhs()
        if type == common_pb2.FieldTypesEnum.Name(common_pb2.DATE_TIME):
            return ner.Ner()
        if type == common_pb2.FieldTypesEnum.Name(common_pb2.NRP):
            return ner.Ner()
        if type == common_pb2.FieldTypesEnum.Name(common_pb2.LOCATION):
            return ner.Ner()
        if type == common_pb2.FieldTypesEnum.Name(common_pb2.PERSON):
            return ner.Ner()

    create = staticmethod(create)


types_refs = {
    common_pb2.FieldTypesEnum.Name(common_pb2.CREDIT_CARD),
    common_pb2.FieldTypesEnum.Name(common_pb2.CRYPTO),
    common_pb2.FieldTypesEnum.Name(common_pb2.DATE_TIME),
    common_pb2.FieldTypesEnum.Name(common_pb2.DOMAIN_NAME),
    common_pb2.FieldTypesEnum.Name(common_pb2.EMAIL_ADDRESS),
    common_pb2.FieldTypesEnum.Name(common_pb2.IBAN_CODE),
    common_pb2.FieldTypesEnum.Name(common_pb2.IP_ADDRESS),
    common_pb2.FieldTypesEnum.Name(common_pb2.NRP),
    common_pb2.FieldTypesEnum.Name(common_pb2.LOCATION),
    common_pb2.FieldTypesEnum.Name(common_pb2.PERSON),
    common_pb2.FieldTypesEnum.Name(common_pb2.US_BANK_NUMBER),
    common_pb2.FieldTypesEnum.Name(common_pb2.US_DRIVER_LICENSE),
    common_pb2.FieldTypesEnum.Name(common_pb2.US_ITIN),
    common_pb2.FieldTypesEnum.Name(common_pb2.US_PASSPORT),
    common_pb2.FieldTypesEnum.Name(common_pb2.PHONE_NUMBER),
    common_pb2.FieldTypesEnum.Name(common_pb2.US_SSN),
    common_pb2.FieldTypesEnum.Name(common_pb2.UK_NHS),
}
