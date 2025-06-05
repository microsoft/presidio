# Azure Health De-Identification Service Integration

## Introduction

The Azure Health De-Identification Service (AHDS) is a cloud-based 
service that provides advanced natural language processing over 
raw text. One of its main functions includes Named Entity Recognition 
(NER), which has the ability to identify different
entities in text and categorize them into pre-defined classes or types.
This document will demonstrate Presidio integration with the Azure Health 
De-Identification Service.

## Supported entity categories in the Azure Health De-Identification API
Azure AI Language supports multiple PII entity categories. The Azure AI Laguage service
runs a predictive model to identify and categorize named entities from an input
document. The service's latest version includes the ability to detect personal (PII)
and health (PHI) information. A list of all supported entities can be found in the
[official documentation](https://learn.microsoft.com/en-us/azure/healthcare-apis/deidentification/overview).

## Prerequisites
To use Azure Health De-Identification with Preisido, an Azure Health De-Identification resource should
first be created under an Azure subscription. Follow the [official documentation](https://learn.microsoft.com/en-us/azure/healthcare-apis/deidentification/quickstart)
for instructions. The endpoint, generated once the resource is created, 
will be used when integrating with Azure Health De-Identification, using a Presidio remote recognizer.

## Azure Health De-Identification Recognizer
[The implementation of a `AzureHealthDeid` recognizer can be found here](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/predefined_recognizers/ahds_recognizer.py).

## How to integrate Azure Health De-Identification into Presidio

1. Install the package with the ahds extra:
  ```sh
  pip install "presidio-analyzer[ahds]"
  ```

2. Define environment variables `AHDS_ENDPOINT`

3. Add the `AzureHealthDeidRecognizer` to the recognizer registry:
  
  ```python
  from presidio_analyzer import AnalyzerEngine
  from presidio_analyzer.predefined_recognizers import AzureHealthDeidRecognizer
    
  ahds = AzureHealthDeidRecognizer()
  
  analyzer = AnalyzerEngine()
  analyzer.registry.add_recognizer(ahds)
  
  analyzer.analyze(text="My email is email@email.com", language="en")
  ```
