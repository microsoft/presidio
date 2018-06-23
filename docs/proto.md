# Protocol Documentation
<a name="top"/>

## Table of Contents

- [analyze.proto](#analyze.proto)
    - [AnalyzeApiRequest](#types.AnalyzeApiRequest)
    - [AnalyzeRequest](#types.AnalyzeRequest)
    - [Results](#types.Results)
  
  
  
    - [AnalyzeService](#types.AnalyzeService)
  

- [anonymize.proto](#anonymize.proto)
    - [AnonymizeApiRequest](#types.AnonymizeApiRequest)
    - [AnonymizeRequest](#types.AnonymizeRequest)
    - [AnonymizeResponse](#types.AnonymizeResponse)
    - [AnonymizeTemplate](#types.AnonymizeTemplate)
    - [Configuration](#types.Configuration)
    - [FieldTypeTransformation](#types.FieldTypeTransformation)
  
  
  
    - [AnonymizeService](#types.AnonymizeService)
  

- [common.proto](#common.proto)
    - [FieldType](#types.FieldType)
    - [Location](#types.Location)
    - [RecordTransformation](#types.RecordTransformation)
    - [RedactValue](#types.RedactValue)
    - [ReplaceValue](#types.ReplaceValue)
    - [Result](#types.Result)
    - [Transformation](#types.Transformation)
  
  
  
  

- [job.proto](#job.proto)
    - [Job](#types.Job)
    - [Schedule](#types.Schedule)
    - [Trigger](#types.Trigger)
  
  
  
  

- [Scalar Value Types](#scalar-value-types)



<a name="analyze.proto"/>
<p align="right"><a href="#top">Top</a></p>

## analyze.proto



<a name="types.AnalyzeApiRequest"/>

### AnalyzeApiRequest



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| text | [string](#string) |  |  |
| analyzeTemplateId | [string](#string) |  |  |






<a name="types.AnalyzeRequest"/>

### AnalyzeRequest



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| value | [string](#string) |  |  |
| fields | [string](#string) | repeated |  |
| minProbability | [string](#string) |  |  |






<a name="types.Results"/>

### Results



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| results | [Result](#types.Result) | repeated |  |





 

 

 


<a name="types.AnalyzeService"/>

### AnalyzeService


| Method Name | Request Type | Response Type | Description |
| ----------- | ------------ | ------------- | ------------|
| Apply | [AnalyzeRequest](#types.AnalyzeRequest) | [Results](#types.AnalyzeRequest) |  |

 



<a name="anonymize.proto"/>
<p align="right"><a href="#top">Top</a></p>

## anonymize.proto



<a name="types.AnonymizeApiRequest"/>

### AnonymizeApiRequest



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| text | [string](#string) |  |  |
| analyzeTemplateId | [string](#string) |  |  |
| anonymizeTemplateId | [string](#string) |  |  |






<a name="types.AnonymizeRequest"/>

### AnonymizeRequest



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| text | [string](#string) |  |  |
| template | [AnonymizeTemplate](#types.AnonymizeTemplate) |  |  |
| results | [Result](#types.Result) | repeated |  |






<a name="types.AnonymizeResponse"/>

### AnonymizeResponse



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| text | [string](#string) |  |  |






<a name="types.AnonymizeTemplate"/>

### AnonymizeTemplate



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| name | [string](#string) |  |  |
| displayName | [string](#string) |  |  |
| description | [string](#string) |  |  |
| createTime | [string](#string) |  |  |
| modifiedTime | [string](#string) |  |  |
| configuration | [Configuration](#types.Configuration) |  |  |






<a name="types.Configuration"/>

### Configuration



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| fieldTypeTransformations | [FieldTypeTransformation](#types.FieldTypeTransformation) | repeated |  |
| recordTransformations | [RecordTransformation](#types.RecordTransformation) | repeated |  |






<a name="types.FieldTypeTransformation"/>

### FieldTypeTransformation



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| fieldTypes | [FieldType](#types.FieldType) | repeated |  |
| transformation | [Transformation](#types.Transformation) |  |  |





 

 

 


<a name="types.AnonymizeService"/>

### AnonymizeService


| Method Name | Request Type | Response Type | Description |
| ----------- | ------------ | ------------- | ------------|
| Apply | [AnonymizeRequest](#types.AnonymizeRequest) | [AnonymizeResponse](#types.AnonymizeRequest) |  |

 



<a name="common.proto"/>
<p align="right"><a href="#top">Top</a></p>

## common.proto



<a name="types.FieldType"/>

### FieldType



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| name | [string](#string) |  |  |
| languageCode | [string](#string) |  |  |






<a name="types.Location"/>

### Location



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| start | [sint32](#sint32) |  |  |
| end | [sint32](#sint32) |  |  |
| length | [sint32](#sint32) |  |  |
| newStart | [sint32](#sint32) |  |  |
| newEnd | [sint32](#sint32) |  |  |
| newLength | [sint32](#sint32) |  |  |






<a name="types.RecordTransformation"/>

### RecordTransformation







<a name="types.RedactValue"/>

### RedactValue







<a name="types.ReplaceValue"/>

### ReplaceValue



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| newValue | [string](#string) |  |  |






<a name="types.Result"/>

### Result



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| value | [string](#string) |  |  |
| fieldType | [string](#string) |  |  |
| probability | [float](#float) |  |  |
| location | [Location](#types.Location) |  |  |
| transformation | [Transformation](#types.Transformation) |  |  |






<a name="types.Transformation"/>

### Transformation



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| newValue | [string](#string) |  |  |
| replaceValue | [ReplaceValue](#types.ReplaceValue) |  |  |
| redactValue | [RedactValue](#types.RedactValue) |  |  |





 

 

 

 



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

