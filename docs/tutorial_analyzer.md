# Using the Analyzer service

Throughout this tutorial, we’ll walk you through the creation of a basic request to the analyzer and anonymizer components.

See [Install Presidio](install.md#L5) for a tutorial on how to install Presidio.

## Analyze your textual data

Analysis could be performed either by using Presidio as a deployed service (Method 1), or using the `presidio-analyzer` python package (Method 2).

### Method 1

First, we need to serve our model. We can do that very easily with (Takes about 10 seconds to load)

  ```sh
  ./presidio-analyzer serve
  ```

Now that our model is up and running, we can send PII text to it. 

*From another shell*

  ```sh
  ./presidio-analyzer analyze --text "John Smith drivers license is AC432223" --fields "PERSON" "US_DRIVER_LICENSE"
  ```

The expected result is:

```json
{
  "analyzeResults": [
    {
      "text": "John Smith",
      "field": {
        "name": "PERSON"
      },
      "score": 0.8500000238418579,
      "location": {
        "end": 10,
        "length": 10,
        "start": 0
      }
    },
    {
      "text": "AC432223",
      "field": {
        "name": "US_DRIVER_LICENSE"
      },
      "score": 0.6499999761581421,
      "location": {
        "start": 30,
        "end": 38,
        "length": 8
      }
    }
  ]
}
```

### Method 2

Use the analyzer Python code by importing `analyzer_engine.py` from `presidio-analyzer/analyzer`

```python
from analyzer import AnalyzerEngine

analyzer = AnalyzerEngine()
results = analyzer.analyze(text="My phone number is 212-555-5555",
                           entities=["PHONE_NUMBER"],
                           language='en',
                           all_fields=False)
print(
    ["Entity: {ent}, score: {score}\n".format(ent=res.entity_type,
                                              score=res.score)
      for res in results])
```