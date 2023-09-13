# Integration with Semantic Kernel Sample

## Intro

This sample shows how presidio can be integrated with semantic kernel to make sure no PII is passed in the prompt and and response.

## Prerequisites

- Install the semantic kernel python package - `python -m pip install semantic-kernel`

## Getting Started

To get started with the demo you will need to provide the credentials for the OpenAI instance. 
Make sure you have an (Open AI API Key)[https://openai.com/api/] or (Azure Open AI service key)[https://learn.microsoft.com/azure/cognitive-services/openai/quickstart?pivots=rest-api]
Copy those keys into a .env file  

Running the demo: `python anonymize-conversation.py`

