from field_types.globally import credit_card, crypto, email, ip, iban, domain, ner
from field_types.us import phone
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
    common_pb2.FieldTypesEnum.Name(common_pb2.PHONE_NUMBER): phone.Phone(),
}
