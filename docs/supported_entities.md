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
|EMAIL_ADDRESS|An email address identifies an email box to which email messages are delivered|Pattern match, context and RFC-822 validation|
|IBAN_CODE|The International Bank Account Number (IBAN) is an internationally agreed system of identifying bank accounts across national borders to facilitate the communication and processing of cross border transactions with a reduced risk of transcription errors.|Pattern match, context and checksum|
|IP_ADDRESS|An Internet Protocol (IP) address (either IPv4 or IPv6).|Pattern match, context and checksum|
|NRP|A person’s Nationality, religious or political group.|Custom logic and context|
|LOCATION|Name of politically or geographically defined location (cities, provinces, countries, international regions, bodies of water, mountains|Custom logic and context|
|PERSON|A full person name, which can include first names, middle names or initials, and last names.|Custom logic and context|
|PHONE_NUMBER|A telephone number|Custom logic, pattern match and context|
|MEDICAL_LICENSE|Common medical license numbers.|Pattern match, context and checksum|
|URL|A URL (Uniform Resource Locator), unique identifier used to locate a resource on the Internet|Pattern match, context and top level url validation|

### USA

|Entity Type|Description|Detection Method|
|--- |--- |--- |
|US_BANK_NUMBER|A US bank account number is between 8 to 17 digits.|Pattern match and context|
|US_DRIVER_LICENSE|A US driver license according to <https://ntsi.com/drivers-license-format/>|Pattern match and context|
|US_ITIN | US Individual Taxpayer Identification Number (ITIN). Nine digits that start with a "9" and contain a "7" or "8" as the 4 digit.|Pattern match and context|
|US_PASSPORT |A US passport number with 9 digits.|Pattern match and context|
|US_SSN|A US Social Security Number (SSN) with 9 digits.|Pattern match and context|

### UK

|Entity Type|Description|Detection Method|
|--- |--- |--- |
|UK_NHS|A UK NHS number is 10 digits.|Pattern match, context and checksum|

### Spain

|Entity Type|Description|Detection Method|
|--- |--- |--- |
|ES_NIF| A spanish NIF number (Personal tax ID) .|Pattern match, context and checksum|

### Italy

|Entity Type|Description|Detection Method|
|--- |--- |--- |
|IT_FISCAL_CODE| An Italian personal identification code. <https://en.wikipedia.org/wiki/Italian_fiscal_code>|Pattern match, context and checksum|
|IT_DRIVER_LICENSE| An Italian driver license number.|Pattern match and context|
|IT_VAT_CODE| An Italian VAT code number |Pattern match, context and checksum|
|IT_PASSPORT|An Italian passport number.|Pattern match and context|
|IT_IDENTITY_CARD|An Italian identity card number. <https://en.wikipedia.org/wiki/Italian_electronic_identity_card>|Pattern match and context|

### Poland

|Entity Type|Description|Detection Method|
|--- |--- |--- |
|PL_PESEL|Polish PESEL number|Pattern match, context and checksum|

### Singapore

|FieldType|Description|Detection Method|
|--- |--- |--- |
|SG_NRIC_FIN| A National Registration Identification Card | Pattern match and context |

### Australia

|FieldType|Description|Detection Method|
|--- |--- |--- |
|AU_ABN| The Australian Business Number (ABN) is a unique 11 digit identifier issued to all entities registered in the Australian Business Register (ABR). | Pattern match, context, and checksum |
|AU_ACN| An Australian Company Number is a unique nine-digit number issued by the Australian Securities and Investments Commission to every company registered under the Commonwealth Corporations Act 2001 as an identifier. | Pattern match, context, and checksum |
|AU_TFN| The tax file number (TFN) is a unique identifier issued by the Australian Taxation Office to each taxpaying entity | Pattern match, context, and checksum |
|AU_MEDICARE| Medicare number is a unique identifier issued by Australian Government that enables the cardholder to receive a rebates of medical expenses under Australia's Medicare system| Pattern match, context, and checksum |

### India
| FieldType  | Description                                                                                                                                                         |Detection Method|
|------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|--- |
| IN_PAN     | The Indian Permanent Account Number (PAN) is a unique 12 character alphanumeric identifier issued to all business and individual entities registered as Tax Payers. | Pattern match, context |
| IN_AADHAAR | Indian government issued unique 12 digit individual identity number                                                                                                 | Pattern match, context, and checksum |
| IN_VEHICLE_REGISTRATION | Indian government issued transport (govt, personal, diplomatic, defence)  vehicle registration number                                                               | Pattern match, context, and checksum |

## Adding a custom PII entity

See [this documentation](analyzer/adding_recognizers.md) for instructions on how to add a new Recognizer for a new type of PII entity.

## Complementing Presidio with Azure AI Language PII

[Azure AI Language PII](https://learn.microsoft.com/en-us/azure/ai-services/language-service/personally-identifiable-information/overview)
 is a cloud-based service that provides Natural Language Processing (NLP) features for detecting PII in text.

A list of supported entities by Azure AI Language PII [can be found here](https://learn.microsoft.com/en-us/azure/ai-services/language-service/personally-identifiable-information/concepts/entity-categories).

To add Azure AI language into Presidio, [see this sample](samples/python/text_analytics/index.md#how-to-integrate-azure-ai-language-into-presidio).

### Connecting to 3rd party PII detectors

See [this documentation](analyzer/adding_recognizers.md#creating-a-remote-recognizer) for instructions on how to implement an external PII detector for a new or existing type of PII entity.
