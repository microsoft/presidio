# Run Presidio With Transformers Models

In the following example you will see how extract PII entities using transformers models.
When initializing the `TransformersRecognizer`, choose from the following options:
1. A string referencing an uploaded model to HuggingFace. Use this url to access all TokenClassification models - https://huggingface.co/models?pipeline_tag=token-classification&sort=downloads

2. Initialize your own TokenClassificationPipeline instance using your custom transformers model and use it for inference.

>**Note**<br>
>For each combination of model & dataset, it is recommend to create a configuration object which >includes setting necessary parameters for getting the correct results. Please reference this [configuraion.py](configuration.py) file for examples.


### Example Code


```python
from configuration import BERT_DEID_CONFIGURATION
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from transformers_recognizer import TransformersRecognizer

model_path = "obi/deid_roberta_i2b2"

supported_entities = ["PERSON", "DATE_TIME", "LOCATION"]
transformers_recognizer = TransformersRecognizer(model_path=model_path, supported_entities=supported_entities)

# This would download a large (~500Mb) model on the first run
transformers_recognizer.load_transformer(**BERT_DEID_CONFIGURATION)

# Add transformers model to the registry
registry = RecognizerRegistry()
registry.add_recognizer(transformers_recognizer)
analyzer = AnalyzerEngine(registry=registry)

sample = "My name is John and I live in NY"
results = analyzer.analyze(sample, language="en",
                            return_decision_process=True,
                            )
print("Found the following entities:")
for result in results:
    print(result, '----', sample[result.start:result.end])
```
