# Recognizers Development - Best Practices and Considerations

Recognizers are the main building blocks in Presidio. Each recognizer is in charge of detecting one or more entities in one or more languages.
Recognizers define the logic for detection, as well as the confidence a prediction receives and a list of words to be used when context is leveraged.

## Implementation Considerations

### Accuracy

Each recognizer, regardless of its complexity, could have false positives and false negatives. When adding new recognizers, we try to balance the effect of each recognizer on the entire system. A recognizer with many false positives would affect the system's usability, while a recognizer with many false negatives might require more work before it can be integrated. For reproducibility purposes, it is be best to note how the recognizer's accuracy was tested, and on which datasets.
For tools and documentation on evaluating and analyzing recognizers, refer to the [presidio-research Github repository](https://github.com/microsoft/presidio-research).

!!! note "Note"
    When contributing recognizers to the Presidio OSS,
    new predefined recognizers should be added to the
    [supported entities list](../supported_entities.md),
    and follow the [contribution guidelines](https://github.com/microsoft/presidio/blob/main/CONTRIBUTING.md).

### Performance

Make sure your recognizer doesn't take too long to process text. Anything above 100ms per request with 100 tokens is probably not good enough.

### Environment

When adding new recognizers that have 3rd party dependencies, make sure that the new dependencies don't interfere with Presidio's dependencies. In the case of a conflict, one can create an isolated model environment (outside the main presidio-analyzer process) and implement a [`RemoteRecognizer`](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/remote_recognizer.py) on the presidio-analyzer side to interact with the model's endpoint. In addition, make sure the license on the 3rd party dependency allows you to use it for any purpose.

## Recognizer Types

Generally speaking, there are three types of recognizers:

### Deny Lists

A deny list is a list of words that should be removed during text analysis. For example, it can include a list of titles (`["Mr.", "Mrs.", "Ms.", "Dr."]` to detect a "Title" entity.)

See [this documentation](index.md#how-to-add-a-new-recognizer) on adding a new recognizer. The [`PatternRecognizer`](/presidio-analyzer/presidio_analyzer/pattern_recognizer.py) class has built-in support for a deny-list input.

### Pattern Based

Pattern based recognizers use regular expressions to identify entities in text.
See [this documentation](adding_recognizers.md) on adding a new recognizer via code.
The [`PatternRecognizer`](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/pattern_recognizer.py) class should be extended.
See some examples here:

!!! example "Examples"
    Examples of pattern based recognizers are the [`CreditCardRecognizer`](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/predefined_recognizers/credit_card_recognizer.py) and [`EmailRecognizer`](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/predefined_recognizers/email_recognizer.py).

### Machine Learning (ML) Based or Rule-Based

Many PII entities are undetectable using naive approaches like deny-lists or regular expressions.
In these cases, we would wish to utilize a Machine Learning model capable of identifying entities in free text, or a rule-based recognizer. There are four options for adding ML and rule based recognizers:

#### Utilize SpaCy or Stanza

Presidio currently uses [spaCy](https://spacy.io/) as a framework for text analysis and Named Entity Recognition (NER), and [stanza](https://stanfordnlp.github.io/stanza/) as an alternative. To avoid introducing new tools, it is recommended to first try to use `spaCy` or `stanza` over other tools if possible.
`spaCy` provides descent results compared to state-of-the-art NER models, but with much better computational performance.
`spaCy` and `stanza` models could be trained from scratch, used in combination with pre-trained embeddings, or retrained to detect new entities.
When integrating such a model into Presidio, a class inheriting from the [`EntityRecognizer`](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/entity_recognizer.py) should be created.

#### Utilize Scikit-learn or Similar

`Scikit-learn` models tend to be fast, but usually have lower accuracy than deep learning methods. However, for well defined problems with well defined features, they can provide very good results.
When integrating such a model into Presidio, a class inheriting from the [`EntityRecognizer`](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/entity_recognizer.py) should be created.

#### Apply Custom Logic

In some cases, rule-based logic provides the best way of detecting entities.
The Presidio `EntityRecognizer` API allows you to use `spaCy`/`stanza` extracted features like lemmas, part of speech, dependencies and more to create your logic. When integrating such logic into Presidio, a class inheriting from the [`EntityRecognizer`](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/entity_recognizer.py) should be created.

#### Deep Learning Based Methods

Deep learning methods offer excellent detection rates for NER.
They are however more complex to train, deploy and tend to be slower than traditional approaches.
When creating a DL based method for PII detection, there are two main alternatives for integrating it with Presidio:

1. Create an external endpoint (either local or remote) which is isolated from the `presidio-analyzer` process. On the `presidio-analyzer` side, one would extend the [`RemoteRecognizer`](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/remote_recognizer.py) class and implement the network interface between `presidio-analyzer` and the endpoint of the model's container.
2. Integrate the model as an additional [`EntityRecognizer`](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/entity_recognizer.py) within the `presidio-analyzer` flow.

!!! attention "Considerations for selecting one option over another"

    - Ease of integration.
    - Runtime considerations (For example if the new model requires a GPU).
    - 3rd party dependencies of the new model vs. the existing `presidio-analyzer` package.
