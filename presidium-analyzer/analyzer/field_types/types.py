from field_types.globally import credit_card, crypto, email, ip
from field_types.us import phone

types_refs = {
    "PHONE_NUMBER": phone.Phone(),
    "CREDIT_CARD": credit_card.CreditCard(),
    "CRYPTO": crypto.Crypto(),
    "EMAIL": email.Email(),
    "IP": ip.Ip(),
}
