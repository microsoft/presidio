# Using GLiNER within Presidio

## What is GLiNER

GLiNER is a Named Entity Recognition (NER) model capable of identifying any entity type using a bidirectional transformer encoder (BERT-like). It provides a practical alternative to traditional NER models, which are limited to predefined entities, and Large Language Models (LLMs) that, despite their flexibility, are costly and large for resource-constrained scenarios.

Paper: [GLiNER: Generalist Model for Named Entity Recognition using Bidirectional Transformer](https://arxiv.org/abs/2311.08526)

Since GLiNER takes as input both the sentence/text and entity types, it can be used for zero-shot named entity recognition. This means that it can recognize entities that were not seen during training.

## PII Detection with GLiNER

GLiNER has a trained PII detection model: 🔍 [`urchade/gliner_multi_pii-v1`](https://huggingface.co/urchade/gliner_multi_pii-v1) *(Apache 2.0)*

This model is capable of recognizing various types of *personally identifiable information* (PII), including but not limited to these entity types: `person`, `organization`, `phone number`, `address`, `passport number`, `email`, `credit card number`, `social security number`, `health insurance id number`, `date of birth`, `mobile phone number`, `bank account number`, `medication`, `cpf`, `driver's license number`, `tax identification number`, `medical condition`, `identity card number`, `national id number`, `ip address`, `email address`, `iban`, `credit card expiration date`, `username`, `health insurance number`, `registration number`, `student id number`, `insurance number`, `flight number`, `landline phone number`, `blood type`, `cvv`, `reservation number`, `digital signature`, `social media handle`, `license plate number`, `cnpj`, `postal code`, `passport_number`, `serial number`, `vehicle registration number`, `credit card brand`, `fax number`, `visa number`, `insurance company`, `identity document number`, `transaction number`, `national health insurance number`, `cvc`, `birth certificate number`, `train ticket number`, `passport expiration date`, and `social_security_number`.

## Using GLiNER with Presidio

Presidio has a built-in `EntityRecognizer` for GLiNER: `GLiNERRecognizer`. This recognizer can be used to detect PII entities in text using the GLiNER model.

### Installation

To use GLiNER with Presidio, you need to install the `presidio-analyzer` with the `gliner` extra:

```bash
pip install 'presidio-analyzer[gliner]'
```

!!! note
    GLiNER only supports python 3.10 and above, while Presidio supports version 3.9 and above.

### Example

```python
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_analyzer.predefined_recognizers import GLiNERRecognizer


# Load a small spaCy model as we don't need spaCy's NER
nlp_engine = NlpEngineProvider(
    nlp_configuration={
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
    }
)

# Create an analyzer engine 
analyzer_engine = AnalyzerEngine()

# Define and create the GLiNER recognizer
entity_mapping = {
    "person": "PERSON",
    "name": "PERSON",
    "organization": "ORGANIZATION",
    "location": "LOCATION"
}

gliner_recognizer = GLiNERRecognizer(
    model_name="urchade/gliner_multi_pii-v1",
    entity_mapping=entity_mapping,
    flat_ner=False,
    multi_label=True,
    map_location="cpu",
)

# Add the GLiNER recognizer to the registry
analyzer_engine.registry.add_recognizer(gliner_recognizer)

# Remove the spaCy recognizer to avoid NER coming from spaCy
analyzer_engine.registry.remove_recognizer("SpacyRecognizer")

# Analyze text
results = analyzer_engine.analyze(
    text="Hello, my name is Rafi Mor, I'm from Binyamina and I work at Microsoft. ", language="en"
)

print(results)
```
