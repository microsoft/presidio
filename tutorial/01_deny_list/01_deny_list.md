# Example 1: Deny-list based PII recognition

In this example, we will pass a short list of tokens which should be marked as PII if detected.
First, let's define the tokens we want to treat as PII. In this case it would be a list of titles:

<!--pytest-codeblocks:cont-->

```python
titles_list = [
    "Sir",
    "Ma'am",
    "Madam",
    "Mr.",
    "Mrs.",
    "Ms.",
    "Miss",
    "Dr.",
    "Professor",
]
```

Second, let's create a `PatternRecognizer` which would scan for those titles, by passing a `deny_list`:

<!--pytest-codeblocks:cont-->

```python
from presidio_analyzer import PatternRecognizer

titles_recognizer = PatternRecognizer(supported_entity="TITLE", deny_list=titles_list)
```

At this point we can call our recognizer directly:

<!--pytest-codeblocks:cont-->

```python
from presidio_analyzer import PatternRecognizer

text1 = "I suspect Professor Plum, in the Dining Room, with the candlestick"
result = titles_recognizer.analyze(text1, entities=["TITLE"])
print(f"Result:\n {result}")
```

Finally, let's add this new recognizer to the list of recognizers used by the Presidio `AnalyzerEngine`:

<!--pytest-codeblocks:cont-->

```python
from presidio_analyzer import AnalyzerEngine

analyzer = AnalyzerEngine()
analyzer.registry.add_recognizer(titles_recognizer)
```

When initializing the `AnalyzerEngine`, Presidio loads all available recognizers,
including the `NlpEngine` used to detect entities, and extract tokens, lemmas and other linguistic features.

Let's run the analyzer with the new recognizer in place:

<!--pytest-codeblocks:cont-->

```python
results = analyzer.analyze(text=text1, language="en")
```

<!--pytest-codeblocks:cont-->

```python
print("Results:")
print(results)
```

As expected, both the name "Plum" and the title were identified as PII:

<!--pytest-codeblocks:cont-->

```python
print("Identified these PII entities:")
for result in results:
    print(f"- {text1[result.start:result.end]} as {result.entity_type}")
```
