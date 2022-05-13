# Example 8: Creating no-code pattern recognizers

No-code pattern recognizers can be helpful in two scenarios:

1. There's an existing set of regular expressions / deny-lists which needs to be added to Presidio.
2. Non-technical team members who require adding logic without writing code.

Regular expression or deny-list based recognizers can be written in a YAML file, and added to the list of recognizers in Presidio.

An example YAML file can be found [here](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/conf/example_recognizers.yaml).

For more information on the schema, see the `PatternRecognizer` definition on the [API Docs](https://microsoft.github.io/presidio/api-docs/api-docs.html#tag/Analyzer)).

Once the YAML file is created, it can be loaded into the `RecognizerRegistry` instance.

This example creates a `RecognizerRegistry` holding only the recognizers in the YAML file:

 <!--pytest-codeblocks:skip-->
``` python
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry

yaml_file = "recognizers.yaml"
registry = RecognizerRegistry()
registry.add_recognizers_from_yaml(yaml_file)

analyzer = AnalyzerEngine(registry=registry)
analyzer.analyze(text="Mr. and Mrs. Smith", language="en")
```

This example adds the new recognizers to the predefined recognizers in Presidio:

 <!--pytest-codeblocks:skip-->
``` python
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry

yaml_file = "recognizers.yaml"  # path to YAML file
registry = RecognizerRegistry()
registry.load_predefined_recognizers()  # Loads all the predefined recognizers (Credit card, phone number etc.)

registry.add_recognizers_from_yaml(yaml_file)

analyzer = AnalyzerEngine()
analyzer.analyze(text="Mr. Plum wrote a book", language="en")
```
