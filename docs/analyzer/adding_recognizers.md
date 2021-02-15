# Supporting new types of PII entities

Presidio can be extended to support detection of new types of PII entities, and to support additional languages.

## Table of contents

- [Introduction to recognizer development](#introduction-to-recognizer-development)
- [Types of recognizer classes in Presidio](#types-of-recognizer-classes-in-presidio)
- [Extending the analyzer for additional PII entities](#extending-the-analyzer-for-additional-pii-entities)
- [Extending to additional languages](#extending-to-additional-languages)

## Introduction to recognizer development

Entity recognizers are Python objects capable of detecting one or more entities in a specific language.
In order to extend Presidio's detection capabilities to new types of PII entities,
these `EntityRecognizer` objects should be added to the existing list of recognizers.

## Types of recognizer classes in Presidio

The following class diagram shows the different types of recognizer families Presidio contains.

![Recognizers class diagram](../assets/recognizers_class_diagram.png)

- The `EntityRecognizer` is an abstract class for all recognizers.
- The `RemoteRecognizer` is an abstract class for calling external PII detectors.
See more info [here](#creating-a-remote-recognizer).
- The `LocalRecognizer` is an abstract class for all recognizers running within the Presidio-analyzer process.
- The `PatternRecognizer` is an class for supporting regex and deny-list based recognition logic,
including validation (e.g., with checksum) and context support. See an example [here](#simple-example).

## Extending the analyzer for additional PII entities

First, a class based on `EntityRecognizer` needs to be created.
Second, the new recognizer should be added to the recognizer registry,
so that the `AnalyzerEngine` would be able to use the new recognizer during analysis.

### Simple example

For simple recognizers based on regular expressions or deny-lists,
we can leverage the provided `PatternRecognizer`:

```python
from presidio_analyzer import PatternRecognizer
titles_recognizer = PatternRecognizer(supported_entity="TITLE",
                                      deny_list=["Mr.","Mrs.","Miss"])
```

Calling the recognizer itself:

```python
titles_recognizer.analyze(text="Mr. Schmidt",entities="TITLE")
```

Adding it to the list of recognizers:

```python
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry

registry = RecognizerRegistry()
registry.load_predefined_recognizers()

# Add the recognizer to the existing list of recognizers
registry.add_recognizer(titles_recognizer)

# Set up analyzer with our updated recognizer registry
analyzer = AnalyzerEngine(registry=registry)

# Run with input text
text="His name is Mr. Jones"
results = analyzer.analyze(text=text, language="en")
print(results)

```

Alternatively, we can add the recognizer directly to the existing registry:

```python
from presidio_analyzer import AnalyzerEngine

analyzer = AnalyzerEngine()

analyzer.registry.add_recognizer(titles_recognizer)

results = analyzer.analyze(text=text,language="en")
print(results)
```

### Creating a new `EntityRecognizer` in code

To create a new recognizer via code:

1. Create a new Python class which implements [LocalRecognizer](../../presidio-analyzer/presidio_analyzer/local_recognizer.py).
(`LocalRecognizer` implements the base [EntityRecognizer](../../presidio-analyzer/presidio_analyzer/entity_recognizer.py) class)

    This class has the following functions:

    i. load: load a model / resource to be used during recognition

    ```python
    def load(self)
    ```

    ii. analyze: The main function to be called for getting entities out of the new recognizer:

    ```python
    def analyze(self, text, entities, nlp_artifacts)
    ```

    Notes:
    1. Each recognizer has access to different NLP assets such as tokens, lemmas, and more.
    These are given through the `nlp_artifacts` parameter.
    Refer to the [source code](../../presidio-analyzer/presidio_analyzer/entity_recognizer.py) for more information.

    2. The `analyze` method should return a list of [RecognizerResult](../../presidio-analyzer/presidio_analyzer/recognizer_result.py).

2. Add it to the recognizer registry using `registry.add_recognizer(my_recognizer)`.

### Creating a remote recognizer

A remote recognizer is an `EntityRecognizer` object interacting with an external service. The external service could be a 3rd party PII detection service or a custom service deployed in parallel to Presidio.

<details>
  <summary>Click here for a reference implementation of a `RemoteRecognizer`</summary>

Here's an illustrative example of how a `RemoteRecognizer` should be implemented. In this example, an external PII detection service exposes two APIs: `detect` and `supported_entities`. The class implemented here, `MyRemoteRecognizer`, uses the `requests` package to call the external service via HTTP.

In this code snippet, we simulate the external PII detector by using the Presidio analyzer. In reality, we would adapt this code to fit the external PII detector we have in hand.

```python
import json
import logging
from typing import List

import requests

from presidio_analyzer import RemoteRecognizer, RecognizerResult
from presidio_analyzer.nlp_engine import NlpArtifacts

logger = logging.getLogger("presidio-analyzer")

import json
import logging
from typing import List

import requests

from presidio_analyzer import RemoteRecognizer, RecognizerResult
from presidio_analyzer.nlp_engine import NlpArtifacts

logger = logging.getLogger("presidio-analyzer")


class ExampleRemoteRecognizer(RemoteRecognizer):
    """
    A reference implementation of a remote recognizer.

    Calls Presidio analyzer as if it was an external remote PII detector
    :param pii_identification_url: Service URL for detecting PII
    :param supported_entities_url: Service URL for getting the supported entities
    by this service
    """

    def __init__(
        self,
        pii_identification_url: str = "https://MYPIISERVICE_URL/detect",
        supported_entities_url: str = "https://MYPIISERVICE_URL/supported_entities",
    ):
        self.pii_identification_url = pii_identification_url
        self.supported_entities_url = supported_entities_url

        super().__init__(
            supported_entities=[], name=None, supported_language="en", version="1.0"
        )

    def load(self) -> None:
        """Call the get_supported_entities API of the external service."""
        try:
            response = requests.get(
                self.supported_entities_url,
                params={"language": self.supported_language},
            )
            self.supported_entities = self._supported_entities_from_response(response)

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get supported entities from external service. {e}")
            self.supported_language = []

    def analyze(
        self, text: str, entities: List[str], nlp_artifacts: NlpArtifacts
    ) -> List[RecognizerResult]:
        """Call an external service for PII detection."""

        payload = {"text": text, "language": self.supported_language}

        response = requests.post(
            self.pii_identification_url,
            json=payload,
            timeout=200,
        )

        results = self._recognizer_results_from_response(response)

        return results

    def get_supported_entities(self) -> List[str]:
        """Return the list of supported entities."""
        return self.supported_entities

    @staticmethod
    def _recognizer_results_from_response(
        response: requests.Response,
    ) -> List[RecognizerResult]:
        """Translate the service's response to a list of RecognizerResult."""
        results = json.loads(response.text)
        recognizer_results = [RecognizerResult(**result) for result in results]

        return recognizer_results

    @staticmethod
    def _supported_entities_from_response(response: requests.Response) -> List[str]:
        """Translate the service's supported entities list to Presidio's."""
        return json.loads(response.text)
```

To call just this recognizer:

```python
if __name__ == "__main__":

    # Illustrative example only: Run Presidio analyzer
    # as if it was an external PII detection mechanism.
    rec = ExampleRemoteRecognizer(
        pii_identification_url="http://localhost:3000/analyze",
        supported_entities_url="http://localhost:3000/supportedentities",
    )

    remote_results = rec.analyze(
        text="My name is David", entities=["PERSON"], nlp_artifacts=None
    )
    print(remote_results)
```

</details>

## Extending to additional languages

For recognizers in new languages, refer to the [languages documentation](languages.md).
