# Custom Fields

Presidio supports custom fields using either online via a simple REST API or by adding new PII recognizers in code. The underlying object behind each field is called a 'Recognizer'. This documentation describes how to add new recognizers by API or code.

## Customization Options

1. [Via API](#via-api)
2. [Via code](#via-code)

## Via Presidio's API <a name="via-api"></a>

a. Getting a recoginzer

```sh
GET <api-service-address>/api/v1/analyzer/recognizers/<recognizer_name>
```

b. Getting all recognizers

```sh
GET <api-service-address>/api/v1/analyzer/recognizers
```

c. Creating a new recoginzer

```sh
POST <api-service-address>/api/v1/analyzer/recognizers/<new_recognizer_name>
```

d. Updating a recoginzer

```sh
PUT <api-service-address>/api/v1/analyzer/recognizers/<new_recognizer_name>
```

### Request structure:

#### Example json:

```json
{
  "value": {
    "entity": "ROCKET",
    "language": "en",
    "patterns": [
      {
        "name": "rocket-recognizer",
        "regex": "\\W*(rocket)\\W*",
        "score": 1
      },
      {
        "name": "projectile-recognizer",
        "regex": "\\W*(projectile)\\W*",
        "score": 1
      }
    ]
  }
}
```

#### Description:

| Field   | Description                | Optional |
| ------- | -------------------------- | -------- |
| `value` | The recognizer json object | no       |

Recognizer format:

| Field            | Description                                                                                                                                               | Optional |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| `entity`         | The name of the new field. e.g. 'ROCKET'                                                                                                                  | no       |
| `language`       | The supported language                                                                                                                                    | no       |
| `patterns`       | A list of regular expressions objects                                                                                                                     | yes      |
| `blacklist`      | A list of words to be identified as PII entities e.g. ["Mr","Mrs","Ms","Miss"]                                                                            | yes      |
| `contextPhrases` | A list of words to be used for improving confidence, in case they are found in vicinity to an identified entity e.g. ["credit-card","credit","cc","amex"] | yes      |

A request should provide either `patterns` or `blacklist` as input.

Regular expression format:

| Field   | Description                                             | Optional |
| ------- | ------------------------------------------------------- | -------- |
| `name`  | The name of this pattern                                | no       |
| `regex` | A regular expression                                    | no       |
| `score` | The score given to entities detected by this recognizer | no       |

d. Update a recoginzer

```sh
PUT <api-service-address>/api/v1/analyzer/recognizers/<recognizer_name>
```

Payload is similar to the one described in `Creating new recognizer`.

e. Delete a recoginzer

```sh
DELETE <api-service-address>/api/v1/analyzer/recognizers/<recognizer_name>
```

f. Using the custom field

After creating a new recognizer, either explicitly state in the templates the newly added entity name, or set allFields to true. For example:

i. `allFields=True`:

```sh
echo -n '{"text":"They sent a rocket to the moon!", "analyzeTemplate":{"allFields":true}  }' | http <api-service-address>/api/v1/projects/<my-project>/analyze
```

ii. Specifically define the recognizers to be used:

```sh
echo -n '{"text":"They sent a rocket to the moon!", "analyzeTemplate":{"fields":[{"name": "ROCKET"}]}}' | http <api-service-address>/api/v1/projects/<my-project>/analyze
```

## Creating a custom recognizer via code <a name="via-code"></a>

Related: [Best practices for developing new recognizers](developing_recognizers.md).

Code based recognizers are written in Python and are a part of the [presidio-analyzer](../presidio-analyzer) module. The main modules in `presidio-analyzer` are the `AnalyzerEngine` and the `RecognizerRegistry`. The `AnalyzerEngine` is in charge of calling each requested recognizer. the `RecognizerRegistry` is in charge of providing the list of predefined and custom recognizers for analysis.

In order to implement a new recognizer by code, follow these two steps:

a. Implement the abstract recognizer class:

Create a new Python class which implements [LocalRecognizer](../presidio-analyzer/presidio_analyzer/local_recognizer.py). `LocalRecognizer` implements the base [EntityRecognizer](../presidio-analyzer/presidio_analyzer/entity_recognizer.py) class. All local recognizers run locally together with all other predefined recognizers as a part of the `presidio-analyzer` Python process. In contrast, `RemoteRecognizer` is a placeholder for recognizers that are external to the `presidio-analyzer` service, for example on a different microservice.

The `EntityRecognizer` abstract class requires the implementation the following methods:

i. initializing a model. Occurs when the `presidio-analyzer` process starts:

```python
def load(self)
```

ii. analyze: The main function to be called for getting entities out of the new recognizer:

```python
def analyze(self, text, entities, nlp_artifacts):
```

The `analyze` method should return a list of [RecognizerResult](../presidio-analyzer/presidio_analyzer/recognizer_result.py). Refer to the [code documentation](../presidio-analyzer/presidio_analyzer/entity_recognizer.py) for more information.

b. Reference and add the new class to the `RecognizerRegistry` module, in the `load_predefined_recognizers` method, which registers all code based recognizers.

c. Note that if by adding the new recognizer, the memory or CPU consumption of the analyzer is expected to grow (such as in the case of adding a new model based recognizer), you should consider updating the pod's resources allocation in [analyzer-deployment.yaml](../charts/presidio/templates/analyzer-deployment.yaml)

d. More information on developing custom recognizers can be found [here](developing_recognizers.md).
