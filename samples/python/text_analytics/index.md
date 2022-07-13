# Azure Text Analytics Integration

## Introduction

Azure Text Analytics is a cloud-based service that provides advanced natural
language processing over raw text. One of its main functions includes 
Named Entity Recognition (NER), which has the ability to identify different
entities in text and categorize them into pre-defined classes or types.
This document will demonstrate Presidio integration with Azure Text Analytics.

## Supported entity categories in the Text Analytics API
Text Analytics supports multiple PII entity categories. The Text Analytics service
runs a predictive model to identify and categorize named entities from an input
document. The service's latest version includes the ability to detect personal (PII)
and health (PHI) information. A list of all supported entities can be found in the
[official documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/text-analytics/named-entity-types?tabs=personal).

## Prerequisites
To use Text Analytics with Preisido, an Azure Text Analytics resource should
first be created under an Azure subscription. Follow the [official documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/text-analytics/how-tos/text-analytics-how-to-call-api?tabs=synchronous#create-a-text-analytics-resource)
for instructions. The key and endpoint, generated once the resource is created, 
will be used when integrating with Text Analytics, using a Presidio Text Analytics recognizer.

## Text Analytics Recognizer
[Sample implementation of a `TextAnalyticsRecognizer`](example_text_analytics_recognizer.py).
The sample suggests an implementation of a [Remote Recognizer](https://microsoft.github.io/presidio/analyzer/adding_recognizers/#creating-a-remote-recognizer)
calling the Text Analytics service REST API. There is also an alternative solution of using `azure-ai-textanalytics` [python package](https://pypi.org/project/azure-ai-textanalytics/),
replacing the client implementation in the example.
The sample reads from a [yaml file](example_text_analytics_entity_categories.yaml), 
defining the entities that should be recognized by Text Analytics, and their corresponding
Preisdio entity types. Use the supported entity categories reference above to extend the 
list of entities defined in the file, with the entities that you want Text Analytics to recognize.
