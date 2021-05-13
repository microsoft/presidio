# Presidio.Model.AnalyzeRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Text** | **string** | The text to analyze | 
**Language** | **string** | Two characters for the desired language in ISO_639-1 format | 
**CorrelationId** | **string** | A correlation id to append to headers and traces | [optional] 
**ScoreThreshold** | **double** | The minimal detection score threshold | [optional] 
**Entities** | **List&lt;string&gt;** | A list of entities to analyze | [optional] 
**ReturnDecisionProcess** | **bool** | Whether to include analysis explanation in the response | [optional] 
**AdHocRecognizers** | [**List&lt;PatternRecognizer&gt;**](PatternRecognizer.md) | list of recognizers to be used in the context of this request only (ad-hoc). | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

