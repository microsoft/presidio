# Example 13: Allow-list to exclude words from being identified as PII

In this example, we will define a list of tokens that should not be marked as PII even if we want to identify others of that kind.

In this example, we will pass a short list of tokens which should not be marked as PII even if detected by one of the recognizers.

<!--pytest-codeblocks:cont-->

```python
websites_list = [
    "bing.com",
    "microsoft.com"
]
```

We will use the built in recognizers that include the `URLRecognizer` and the NLP model `EntityRecognizer` and see the default functionality if we don't specify any list of words for the detector to allow to keep in the text.

<!--pytest-codeblocks:cont-->

```python
from presidio_analyzer import AnalyzerEngine
text1 = "My favorite website is bing.com, his is microsoft.com"
analyzer = AnalyzerEngine()
result = analyzer.analyze(text = text1, language = 'en')
print(f"Result: \n {result}")
```

To specify an allow list we just pass a list of values we want to keep as a parameter to call to `analyze`. Now we can see that in the results, `bing.com` is no longer being recognized as a PII item, only `microsoft.com` is still recognized since we did include it in the allow list.

<!--pytest-codeblocks:cont-->

```python

result = analyzer.analyze(text = text1, language = 'en', allow_list = ["bing.com"] )
print(f"Result:\n {result}")
```
