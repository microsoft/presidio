# Protocol Documentation
<a name="top"/>

## Table of Contents

- [analyze.proto](#analyze.proto)
    - [AnalyzeApiRequest](#types.AnalyzeApiRequest)
    - [AnalyzeRequest](#types.AnalyzeRequest)
    - [AnalyzeResponse](#types.AnalyzeResponse)
  
  
  
    - [AnalyzeService](#types.AnalyzeService)
  

- [anonymize.proto](#anonymize.proto)
    - [AnonymizeApiRequest](#types.AnonymizeApiRequest)
    - [AnonymizeRequest](#types.AnonymizeRequest)
    - [AnonymizeResponse](#types.AnonymizeResponse)
  
  
  
    - [AnonymizeService](#types.AnonymizeService)
  

- [common.proto](#common.proto)
    - [AnalyzeResult](#types.AnalyzeResult)
    - [FieldType](#types.FieldType)
    - [Location](#types.Location)
  
    - [FieldTypeNames](#types.FieldTypeNames)
  
  
  

- [job.proto](#job.proto)
    - [Job](#types.Job)
    - [Schedule](#types.Schedule)
    - [Trigger](#types.Trigger)
  
  
  
  

- [template.proto](#template.proto)
    - [AnalyzeTemplate](#types.AnalyzeTemplate)
    - [AnonymizeTemplate](#types.AnonymizeTemplate)
    - [FieldTypeTransformation](#types.FieldTypeTransformation)
    - [RedactValue](#types.RedactValue)
    - [ReplaceValue](#types.ReplaceValue)
    - [Transformation](#types.Transformation)
  
  
  
  

- [Scalar Value Types](#scalar-value-types)



<a name="analyze.proto"/>
<p align="right"><a href="#top">Top</a></p>

## analyze.proto



<a name="types.AnalyzeApiRequest"/>

### AnalyzeApiRequest
AnalyzeApiRequest represents the request to the API HTTP service


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| text | [string](#string) |  |  |
| analyzeTemplateId | [string](#string) |  |  |






<a name="types.AnalyzeRequest"/>

### AnalyzeRequest
AnalyzeRequest represents the request to the analyze service via GRPC


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| value | [string](#string) |  |  |
| analyzeTemplate | [AnalyzeTemplate](#types.AnalyzeTemplate) |  |  |
| minProbability | [string](#string) |  |  |






<a name="types.AnalyzeResponse"/>

### AnalyzeResponse
AnalyzeResponse represents the analyze service response


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| analyzeResults | [AnalyzeResult](#types.AnalyzeResult) | repeated |  |





 

 

 


<a name="types.AnalyzeService"/>

### AnalyzeService


| Method Name | Request Type | Response Type | Description |
| ----------- | ------------ | ------------- | ------------|
| Apply | [AnalyzeRequest](#types.AnalyzeRequest) | [AnalyzeResponse](#types.AnalyzeRequest) |  |

 



<a name="anonymize.proto"/>
<p align="right"><a href="#top">Top</a></p>

## anonymize.proto



<a name="types.AnonymizeApiRequest"/>

### AnonymizeApiRequest
AnonymizeApiRequest represents the request to the API HTTP service


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| text | [string](#string) |  |  |
| analyzeTemplateId | [string](#string) |  |  |
| anonymizeTemplateId | [string](#string) |  |  |






<a name="types.AnonymizeRequest"/>

### AnonymizeRequest
AnonymizeRequest represents the request to the anonymize service via GRPC


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| text | [string](#string) |  |  |
| template | [AnonymizeTemplate](#types.AnonymizeTemplate) |  |  |
| analyzeResults | [AnalyzeResult](#types.AnalyzeResult) | repeated |  |






<a name="types.AnonymizeResponse"/>

### AnonymizeResponse
AnonymizeResponse represents the anonymize service response


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| text | [string](#string) |  |  |





 

 

 


<a name="types.AnonymizeService"/>

### AnonymizeService


| Method Name | Request Type | Response Type | Description |
| ----------- | ------------ | ------------- | ------------|
| Apply | [AnonymizeRequest](#types.AnonymizeRequest) | [AnonymizeResponse](#types.AnonymizeRequest) |  |

 



<a name="common.proto"/>
<p align="right"><a href="#top">Top</a></p>

## common.proto



<a name="types.AnalyzeResult"/>

### AnalyzeResult



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| text | [string](#string) |  |  |
| fieldType | [string](#string) |  |  |
| probability | [float](#float) |  |  |
| location | [Location](#types.Location) |  |  |






<a name="types.FieldType"/>

### FieldType



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| name | [FieldTypeNames](#types.FieldTypeNames) |  |  |
| languageCode | [string](#string) |  |  |






<a name="types.Location"/>

### Location



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| start | [sint32](#sint32) |  |  |
| end | [sint32](#sint32) |  |  |
| length | [sint32](#sint32) |  |  |
| newStart | [sint32](#sint32) |  | Not used in the template |
| newEnd | [sint32](#sint32) |  | Not used in the template |
| newLength | [sint32](#sint32) |  | Not used in the template |





 


<a name="types.FieldTypeNames"/>

### FieldTypeNames


| Name | Number | Description |
| ---- | ------ | ----------- |
| CREDIT_CARD | 0 |  |
| CRYPTO | 1 |  |
| DATE_TIME | 2 |  |
| DOMAIN_NAME | 3 |  |
| EMAIL_ADDRESS | 4 |  |
| IBAN_CODE | 5 |  |
| IP_ADDRESS | 6 |  |
| NRP | 7 |  |
| LOCATION | 8 |  |
| PERSON | 9 |  |
| PHONE_NUMBER | 10 |  |


 

 

 



<a name="job.proto"/>
<p align="right"><a href="#top">Top</a></p>

## job.proto



<a name="types.Job"/>

### Job



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| name | [string](#string) |  |  |
| description | [string](#string) |  |  |
| trigger | [Trigger](#types.Trigger) |  |  |






<a name="types.Schedule"/>

### Schedule



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| recurrencePeriodDuration | [string](#string) |  |  |






<a name="types.Trigger"/>

### Trigger



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| schedule | [Schedule](#types.Schedule) |  |  |





 

 

 

 



<a name="template.proto"/>
<p align="right"><a href="#top">Top</a></p>

## template.proto



<a name="types.AnalyzeTemplate"/>

### AnalyzeTemplate
AnalyzeTemplate represents the analyze service template definition


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| fields | [string](#string) | repeated |  |






<a name="types.AnonymizeTemplate"/>

### AnonymizeTemplate
AnonymizeTemplate represents the anonymize service template definition


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| name | [string](#string) |  |  |
| displayName | [string](#string) |  |  |
| description | [string](#string) |  |  |
| createTime | [string](#string) |  |  |
| modifiedTime | [string](#string) |  |  |
| fieldTypeTransformations | [FieldTypeTransformation](#types.FieldTypeTransformation) | repeated |  |






<a name="types.FieldTypeTransformation"/>

### FieldTypeTransformation
FieldTypeTransformation represents the transformation for array of fields types


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| fields | [FieldType](#types.FieldType) | repeated |  |
| transformation | [Transformation](#types.Transformation) |  |  |






<a name="types.RedactValue"/>

### RedactValue







<a name="types.ReplaceValue"/>

### ReplaceValue



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| newValue | [string](#string) |  |  |






<a name="types.Transformation"/>

### Transformation
Transformation represents the transformation type


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| newValue | [string](#string) |  | Not used in the template |
| replaceValue | [ReplaceValue](#types.ReplaceValue) |  |  |
| redactValue | [RedactValue](#types.RedactValue) |  |  |





 

 

 

 



## Scalar Value Types

| .proto Type | Notes | C++ Type | Java Type | Python Type |
| ----------- | ----- | -------- | --------- | ----------- |
| <a name="double" /> double |  | double | double | float |
| <a name="float" /> float |  | float | float | float |
| <a name="int32" /> int32 | Uses variable-length encoding. Inefficient for encoding negative numbers – if your field is likely to have negative values, use sint32 instead. | int32 | int | int |
| <a name="int64" /> int64 | Uses variable-length encoding. Inefficient for encoding negative numbers – if your field is likely to have negative values, use sint64 instead. | int64 | long | int/long |
| <a name="uint32" /> uint32 | Uses variable-length encoding. | uint32 | int | int/long |
| <a name="uint64" /> uint64 | Uses variable-length encoding. | uint64 | long | int/long |
| <a name="sint32" /> sint32 | Uses variable-length encoding. Signed int value. These more efficiently encode negative numbers than regular int32s. | int32 | int | int |
| <a name="sint64" /> sint64 | Uses variable-length encoding. Signed int value. These more efficiently encode negative numbers than regular int64s. | int64 | long | int/long |
| <a name="fixed32" /> fixed32 | Always four bytes. More efficient than uint32 if values are often greater than 2^28. | uint32 | int | int |
| <a name="fixed64" /> fixed64 | Always eight bytes. More efficient than uint64 if values are often greater than 2^56. | uint64 | long | int/long |
| <a name="sfixed32" /> sfixed32 | Always four bytes. | int32 | int | int |
| <a name="sfixed64" /> sfixed64 | Always eight bytes. | int64 | long | int/long |
| <a name="bool" /> bool |  | bool | boolean | boolean |
| <a name="string" /> string | A string must always contain UTF-8 encoded or 7-bit ASCII text. | string | String | str/unicode |
| <a name="bytes" /> bytes | May contain any arbitrary sequence of bytes. | string | ByteString | str |

