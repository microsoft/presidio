# Presidio.Model.Anonymizer

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Type** | **string** | encrypt | 
**NewValue** | **string** | The string to replace with | 
**MaskingChar** | **string** | The replacement character | 
**CharsToMask** | **int** | The amount of characters that should be replaced | 
**FromEnd** | **bool** | Whether to mask the PII from it&#39;s end | [optional] [default to false]
**HashType** | **string** | The hashing algorithm | [optional] [default to HashTypeEnum.Md5]
**Key** | **string** | Cryptographic key of length 128, 192 or 256 bits, in a string format | 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

