# Contributing to Presidio

:tada: Thanks for taking the time to contribute! :tada:

The following is a set of guidelines for contributing to Presidio. 

## What do I need to know before I get started?
### Project Presidio
Presidio is a community project aimed at helping everyone handle their private data and make the world a safer place.
Presidio is both a framework and a system. It's a framework in a sense that you could take code parts from it, extend, customize and plug somewhere. It's also a system you could take as a whole or in parts and deploy locally, on-prem on in the cloud, especially when leveraging Kubernetes.
When contributing to presidio, it's important to keep this in mind, as some "framework" contributions might not be suitable for a deployment, or vice-versa.

### Getting started with the code
To get started, refer to the documentation for [setting up a development environment](docs/development.md).

### How can I contribute?
- [General contribution guidelines](#general-contribution-guidlines)
- [Adding new recognizers for new PII types](#adding-new-recognizers-for-new-pii-types)
  * [General note on adding recognizers](#general-note-on-adding-recognizers)
  * [Types of recognizers](#types-of-recognizers)
- [Adding new connectors](#adding-new-connectors)
- [Bug fixing and general improvement](#bug-fixing-and-general-improvement)

### General contribution guidelines
All contributions should be documented, tested and linted. All unit and functional tests must succeed prior to an acception of a contribution. 
In order for a pull request to be accepted, the CI (containing unit tests, functional tests and linting) needs to succeed, in addition to approvals from two core contributors.
### How to test?

- For Go, the official methods for testing are used. see https://golang.org/pkg/testing/
- For Python, Presidio leverages `pytest`, `pylint` and `flake8`. See [this tutorial](docs/development.md#dev-python) on more information on testing the presidio-analyzer module.

Please make sure all tests pass prior to submitting a pull request.



### Adding new recognizers for new PII types
Adding a new recognizer is a great way to improve Presidio. A new capability to detect a new type of PII entity improves Presidio's coverage and makes private data less accessible.

#### General note on adding recognizers
1. Accuracy:

Each recognizer, regardless of its complexity, could have false positives and false negatives. When adding new recognizers, we try to balance the effect of each recognizer on the entire system.
A recognizer with many false positives would affect the system's usability, while a recognizer with many false negatives might require more work before it can be integrated.
We are working on a tool to automatically test new recognizers. In the mean time, it would be best if you clarified how you tested the recognizer's accuracy, and what datasets you've used.

2. Performance:

Make sure your recognizer doesn't take too long to process text. Anything above 100ms per request with 100 tokens is probably not good enough.

3. Environment:

When adding new recognizers that have 3rd party dependencies, make sure that the new dependencies don't interfere with Presidio's dependencies.
In the case of a conflict, one can create an isolated model environment (in a sidecar container or external endpoint) and implement a [RemoteRecognizer](presidio-analyzer/analyzer/remote_recognizer.py) on presidio's side to interact with the model's endpoint.
In addition, make sure the license on the 3rd party dependency allows you to use it for any purpose.


#### Types of recognizers
Generally speaking, there are three types of recognizers:

1. Black lists

A black list is a list of words that should be removed during text analysis. For example, a list of titles (`["Mr.", "Mrs.", "Ms."]` etc.)
This type of recognizer could be added via API or code. In case of contribution, a code-based recognizer is a better option as it gets added to the list of predefined recognizers already implemented in Presidio.
See [this documentation](docs/custom_fields.md#via-code) on adding a new recognizer via code. The [PatternRecognizer](presidio-analyzer/analyzer/pattern_recognizer.py) class already has support for a black-list input.

2. Pattern based

Pattern based recognizers use regular expressions to identify entities in text. 
This type of recognizer could be added by API or code. In case of contribution, a code-based recognizer is a better option as it gets added to the list of predefined recognizers already implemented in Presidio.
See [this documentation](docs/custom_fields.md#via-code) on adding a new recognizer via code. The [PatternRecognizer](presidio-analyzer/analyzer/pattern_recognizer.py) class should be extended.
See some examples here:
  - [Credit card recognizer](presidio-analyzer/analyzer/predefined_recognizers/credit_card_recognizer.py)
  - [Email recognizer](presidio-analyzer/analyzer/predefined_recognizers/email_recognizer.py)

3. Machine Learning (ML) based or rule-based

Many PII entites are undetectable using naive approaches like black-lists or regular expressions. In these cases, we would wish to utilize a Machine Learning model capabable of identifying entities in text, or a rule-based recognizer.
There are four options for adding ML and rule based recognizers:

   - Utilize spaCy:

   Presidio currently uses [spaCy](https://spacy.io/) as a framework for text analysis and Named Entity Recognition (NER). As we prefer to use the existing tools, it would be best to contribute ML models that are based on spaCy. spaCy provides descent results compared to state-of-the-art NER models, but with much better computational performance. spaCy could be trained from scratch, used in combination with pre-trained embeddings, or retrained to detect new entities. When building such model, you would need to extend the [EntityRecognizer](presidio-analyzer/analyzer/entity_recognizer.py) class.
   
   - Utilize Scikit-learn or similar
   
   Scikit-learn models tend to be fast, but usually have lower accuracy than deep learning methods. However, for well defined problems with well defined features, they can provide very good results.
   Since deep learning models tend to be complex and slow, we encourage you to first test a traditional approach (like Conditional Random Fields) before going directly into state-of-the-art *Sesame-Street* character based models... 
   When building such model, you would need to extend the [EntityRecognizer](presidio-analyzer/analyzer/entity_recognizer.py) class.

   - Use custom logic

   In some cases, rule-based logic provides the best way of detecting entities. The Presidio EntityRecognizer API allows you to use spaCy extracted features like lemmas, part of speech, dependencies and more to create your logic. When building such model, you would need to extend the [EntityRecognizer](presidio-analyzer/analyzer/entity_recognizer.py) class.

   - Deep learning based methods

   Deep learning methods offer excellent detection rates for NER. They are however more complex to train, deploy and tend to be slower than traditional approaches. When contributing a DL based method, the best option would be to create a sidecar container which is isolated from the presidio-analyzer container. On the `presidio-analyzer` side, one would extend the [RemoteRecognizer](presidio-analyzer/analyzer/remote_recognizer.py) class and implement the network interface between `presidio-analyzer` and the endpoint of the model's container.

#### Configuring new recognizers

New predefined recognizers should also be listed in the field types list Presidio supports here: https://github.com/microsoft/presidio/blob/master/docs/field_types.md and added to the [proto files here](https://github.com/microsoft/presidio-genproto/blob/1c667b8695755a4c4bbe386cedee4649f239c7c3/src/common.proto#L13)

### Adding new connectors

Presidio's strength lies in its ability to be completely pluggable and customizable. Adding new types of databases, stream-analytics engines and data stores is extremely useful for many users.
While we're working on adding more documentation on this type of customization, you can refer to these documents and resources:
1. Scheduler

   - The [scheduler documentation](docs/tutorial_scheduler.md) describes how to configure the data source and target for a periodic job

2. Templates for source, target and stream configurations and service definitions, on the [presidio-genproto](https://github.com/microsoft/presidio-genproto) repo. For example: 

	- [data sink protocols](https://github.com/microsoft/presidio-genproto/blob/master/src/datasink.proto). Specifically, the [DatasinkTypesEnum](https://github.com/microsoft/presidio-genproto/blob/1734e2635c253f79e4c44398315d92fe9d084601/src/datasink.proto#L37)
	- [S3 template](https://github.com/microsoft/presidio-genproto/blob/1734e2635c253f79e4c44398315d92fe9d084601/src/template.proto#L158)
	- [Kafka template](https://github.com/microsoft/presidio-genproto/blob/1734e2635c253f79e4c44398315d92fe9d084601/src/template.proto#L204)

3. Existing implementations

	- [Streams](presidio-datasink/cmd/presidio-datasink/stream/stream.go)
	- [SQL](presidio-datasink/cmd/presidio-datasink/database/database.go)
	
### Bug fixing and general improvement

Please review the open [issues on Github](https://github.com/microsoft/presidio/issues) for known bugs and feature requests. We sometimes add 'good first issue' labels on those we believe are simpler, and 'advanced' labels on those which require more work or multiple changes across the solution.
