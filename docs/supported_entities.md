# PII entities supported by Presidio

Presidio contains predefined recognizers for PII entities.
This page describes the different entities Presidio can detect and the method Presidio employs to detect those.

In addition, Presidio allows you to add custom entity recognizers.
For more information, refer to the [adding new recognizers documentation](analyzer/adding_recognizers.md).

## List of supported entities

### Global

|Entity Type | Description | Detection Method |
| --- | --- | --- |
|CREDIT_CARD |A credit card number is between 12 to 19 digits. <https://en.wikipedia.org/wiki/Payment_card_number>|Pattern match and checksum|
|CRYPTO|A Crypto wallet number. Currently only Bitcoin address is supported|Pattern match, context and checksum|
|DATE_TIME|Absolute or relative dates or periods or times smaller than a day.|Pattern match and context|
|DOMAIN_NAME|A domain name as defined by the DNS standard.|Pattern match, context and top level domain validation|
|EMAIL_ADDRESS|An email address identifies an email box to which email messages are delivered|Pattern match, context and RFC-822 validation|
|IBAN_CODE|The International Bank Account Number (IBAN) is an internationally agreed system of identifying bank accounts across national borders to facilitate the communication and processing of cross border transactions with a reduced risk of transcription errors.|Pattern match, context and checksum|
|IP_ADDRESS|An Internet Protocol (IP) address (either IPv4 or IPv6).|Pattern match, context and checksum|
|NRP|A person’s Nationality, religious or political group.|Custom logic and context|
|LOCATION|Name of politically or geographically defined location (cities, provinces, countries, international regions, bodies of water, mountains|Custom logic and context|
|PERSON|A full person name, which can include first names, middle names or initials, and last names.|Custom logic and context|
|PHONE_NUMBER|A telephone number|Custom logic, pattern match and context|
|MEDICAL_LICENSE|Common medical license numbers.|Pattern match, context and checksum|

### USA

|FieldType|Description|Detection Method|
|--- |--- |--- |
|US_BANK_NUMBER|A US bank account number is between 8 to 17 digits.|Pattern match and context|
|US_DRIVER_LICENSE|A US driver license according to <https://ntsi.com/drivers-license-format/>|Pattern match and context|
|US_ITIN | US Individual Taxpayer Identification Number (ITIN). Nine digits that start with a "9" and contain a "7" or "8" as the 4 digit.|Pattern match and context|
|US_PASSPORT |A US passport number with 9 digits.|Pattern match and context|
|US_SSN|A US Social Security Number (SSN) with 9 digits.|Pattern match and context|

### UK

|FieldType|Description|Detection Method|
|--- |--- |--- |
|UK_NHS|A UK NHS number is 10 digits.|Pattern match, context and checksum|

### Spain

|FieldType|Description|Detection Method|
|--- |--- |--- |
|NIF| A spanish NIF number (Personal tax ID) .|Pattern match, context and checksum|

### Singapore

|FieldType|Description|Detection Method|
|--- |--- |--- |
|FIN/NRIC| A National Registration Identification Card | Pattern match and context |

## Adding a custom PII entity

See [this documentation](analyzer/adding_recognizers.md) for instructions on how to add a new Recognizer for a new type of PII entity.

### Connecting to 3rd party PII detectors

See [this documentation](analyzer/adding_recognizers.md#creating-a-remote-recognizer) for instructions on how to implement an external PII detector for a new or existing type of PII entity.
