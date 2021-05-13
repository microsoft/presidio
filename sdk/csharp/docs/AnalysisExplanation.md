# Presidio.Model.AnalysisExplanation

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Recognizer** | **string** | Name of recognizer that made the decision | [optional] 
**PatternName** | **string** | name of pattern (if decision was made by a PatternRecognizer) | [optional] 
**Pattern** | **string** | Regex pattern that was applied (if PatternRecognizer) | [optional] 
**OriginalScore** | **double** | Recognizer&#39;s confidence in result | [optional] 
**Score** | **double** | The PII detection score | [optional] 
**TextualExplanation** | **string** | Free text for describing a decision of a logic or model | [optional] 
**ScoreContextImprovement** | **double** | Difference from the original score | [optional] 
**SupportiveContextWord** | **string** | The context word which helped increase the score | [optional] 
**ValidationResult** | **double** | Result of a validation (e.g. checksum) | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

