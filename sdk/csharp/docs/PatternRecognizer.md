# Presidio.Model.PatternRecognizer
A regular expressions or deny-list based recognizer

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Name** | **string** | Name of recognizer | [optional] 
**SupportedLanguage** | **string** | Language code supported by this recognizer | [optional] 
**Patterns** | [**List&lt;Pattern&gt;**](Pattern.md) | List of type Pattern containing regex expressions with additional metadata. | [optional] 
**DenyList** | **List&lt;string&gt;** | List of words to be returned as PII if found. | [optional] 
**Context** | **List&lt;string&gt;** | List of words to be used to increase confidence if found in the vicinity of detected entities. | [optional] 
**SupportedEntity** | **string** | The name of entity this ad hoc recognizer detects | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

