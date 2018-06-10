from field_types.globally import credit_card, crypto, email, ip, iban, domain, ner
from field_types.us import phone

types_refs = {
    "CREDIT_CARD": credit_card.CreditCard(),
    "CRYPTO": crypto.Crypto(),
    "DATE_TIME": ner.Ner(),
    "DOMAIN_NAME": domain.Domain(),
    "EMAIL_ADDRESS": email.Email(),
    "IBAN_CODE": iban.Iban(),
    "IP_ADDRESS": ip.Ip(),
    "NRP": ner.Ner(),
    "LOCATION": ner.Ner(),
    "PERSON": ner.Ner(),
    "PHONE_NUMBER": phone.Phone(),
}
