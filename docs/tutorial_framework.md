# Framework Tutorial

Throughout this tutorial, we’ll walk you through the creation of a basic request to the analyzer and anonymizer components.

See [Install Presidio](install.md#L5) for a tutorial on how to install Presidio.

## Analyze your text data

First, we need to serve our model. We can do that very easily with (Takes about 10 seconds to load)

```
$ ./presidio-analyzer serve
```

Now that our model is up and running, we can send PII text to it. 

*From another shell*
```
$ ./presidio-analyzer analyze --text "John Smith drivers license is AC432223" --fields "PERSON" "US_DRIVER_LICENSE"
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
