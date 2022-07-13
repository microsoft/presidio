# Example 9: Ad-hoc recognizers

In addition to recognizers in code or in a YAML file, it is possible to create ad-hoc recognizers via the Presidio Analyzer API for regex and deny-list based logic.
These recognizers, in JSON form, are added to the `/analyze` request and are only used in the context of this request.

!!! note "Note"
    These ad-hoc recognizers could be useful if Presidio is already deployed, but requires additional detection logic to be added.

- The json structure for a *regex ad-hoc recognizer* is the following:

    ```json
    {
        "text": "John Smith drivers license is AC432223. Zip code: 10023",
        "language": "en",
        "ad_hoc_recognizers":[
            {
            "name": "Zip code Recognizer",
            "supported_language": "en",
            "patterns": [
                {
                "name": "zip code (weak)", 
                "regex": "(\\b\\d{5}(?:\\-\\d{4})?\\b)", 
                "score": 0.01
                }
            ],
            "context": ["zip", "code"],
            "supported_entity":"ZIP"
            }
        ]
    }
    ```

- The json structure for *deny-list based recognizers* is the following:

    ```json
    {
        "text": "Mr. John Smith's drivers license is AC432223",
        "language": "en",
        "ad_hoc_recognizers":[
            {
            "name": "Mr. Recognizer",
            "supported_language": "en",
            "deny_list": ["Mr", "Mr.", "Mister"],
            "supported_entity":"MR_TITLE"
            },
            {
            "name": "Ms. Recognizer",
            "supported_language": "en",
            "deny_list": ["Ms", "Ms.", "Miss", "Mrs", "Mrs."],
            "supported_entity":"MS_TITLE"
            }
        ]
    }
    ```

In both examples, the `/analyze` request is extended with a list of `ad_hoc_recognizers`, which could be either `patterns`, `deny_list` or both.

Example call to the `/analyze` service:

``` json
{
  "text": "John Smith drivers license is AC432223 and the zip code is 12345",
  "language": "en",
  "return_decision_process": false,
  "correlation_id": "123e4567-e89b-12d3-a456-426614174000",
  "score_threshold": 0.6,
  "entities": [
    "US_DRIVER_LICENSE",
    "ZIP"
  ],
  "trace": false,
  "ad_hoc_recognizers": [
    {
      "name": "Zip code Recognizer",
      "supported_language": "en",
      "patterns": [
        {
          "name": "zip code (weak)",
          "regex": "(\\b\\d{5}(?:\\-\\d{4})?\\b)",
          "score": 0.01
        }
      ],
      "context": [
        "zip",
        "code"
      ],
      "supported_entity": "ZIP"
    }
  ]
}
```

For more examples of deny-list recognizers, see [this sample](../samples/python/Anonymizing%20known%20values.ipynb).
