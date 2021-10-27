# Frequently Asked Questions (FAQ)

## What is Presidio?

Presidio (Origin from Latin praesidium ‘protection, garrison’) helps to ensure sensitive data is properly managed and governed. It provides fast identification and anonymization modules for private entities in text and images. It is fully customizable and pluggable, can be adapted it to your needs and be deployed into various environments.

!!! note "Note"
    Presidio is a library or SDK rather than a service. It is meant to be customized to the user's or organization's specific needs.

## Why did Microsoft create Presidio?

Proper handling of private and sensitive data is a major issue across many customers and industries. By developing Presidio, our goals are:

1. Allow organizations to preserve privacy in a simpler way by democratizing de-identification technologies and introducing transparency in decisions.
2. Embrace extensibility and customizability to a specific business need.
3. Facilitate both fully automated and semi-automated PII de-identification flows on multiple platforms.

## How can I start using Presidio?

1. Check out the [installation docs](https://microsoft.github.io/presidio/installation/).
2. Take a look at the [different samples](https://microsoft.github.io/presidio/samples/).
3. Try the [demo website](https://aka.ms/presidio-demo).

## What are the main building blocks in Presidio?

Presidio is a suite built of several packages and building blocks:

1. [Presidio Analyzer](https://microsoft.github.io/presidio/analyzer/): a package for detecting PII entities in natural language.
2. [Presidio Anonymizer](https://microsoft.github.io/presidio/anonymizer/): a package for manipulating PII entities in text (e.g. remove, redact, hash, encrypt).
3. [Presidio Image Redactor](https://microsoft.github.io/presidio/image-redactor/): A package for detecting PII entities in image using OCR.
4. A set of sample deployments as Python packages or Docker containers for Kubernetes, Azure Data Factory, Spark and more.

## How can Presidio be customized to my needs?

Users can customize Presidio in multiple ways:

1. Create new or updated PII recognizers ([docs](https://microsoft.github.io/presidio/analyzer/adding_recognizers/)).
2. Adapt Presidio to new languages ([docs](https://microsoft.github.io/presidio/analyzer/languages/)).
3. Leverage state of the art Named Entity Recognition models ([docs](https://microsoft.github.io/presidio/analyzer/customizing_nlp_models/)).
4. Add new types of anonymizers ([docs](https://microsoft.github.io/presidio/anonymizer/adding_operators/)).
5. Create PII analysis and anonymization pipelines on different environments using Docker or Python ([samples](https://microsoft.github.io/presidio/samples/)).

And more.

## What's the difference between Presidio and different PII detection services like Azure Text Analytics and Amazon Comprehend?

In a nutshell, Presidio is a library which is meant to be customized, whereas different SaaS tools for PII detection have less customization capabilities. Most of these SaaS offerings use dedicated ML models and other logic for PII detection and often have better entity coverage or accuracy than Presidio.

Based on our internal research, leveraging Presidio in parallel to 3rd party PII detection services like Azure Text Analytics can bring optimal results mainly when the data in hand has entity types or values not supported by the service. ([see example here](https://microsoft.github.io/presidio/samples/python/text_analytics/)).

## What NLP frameworks does Presidio support?

Presidio supports spaCy version 3+ for Named Entity Recognition, tokenization, lemmatization and more. We also support [Stanza](https://stanfordnlp.github.io/stanza/) using the [spacy-stanza](https://spacy.io/universe/project/spacy-stanza) package, and it is further possible to create PII recognizers leveraging other frameworks like [transformers](https://huggingface.co/transformers/usage.html#named-entity-recognition) or [Flair](https://github.com/flairNLP/flair).

For more information, see the [docs](https://microsoft.github.io/presidio/analyzer/customizing_nlp_models/).

## What can I do if Presidio does not detect some of the PII entities in my data?

Presidio comes loaded with several PII recognizers (see [list here](https://microsoft.github.io/presidio/supported_entities/)), however its main strength lies in its customization capabilities to new entities, specific datasets, languages or use cases. For a recommended process for improving detection accuracy, see [these guidelines](https://github.com/microsoft/presidio/discussions/767#discussion-3567223).

## What can I do if Presidio falsely detects text as PII entities?

Some PII recognizers are less accurate than others. A driver's license number, for example, could be any 9-digit number. While Presidio leverages context words and other logic to improve the detection quality, it could still falsely detect non-entity values as PII entities.

In order to avoid false positives, one could try to:

1. Change the acceptance threshold, which defines what is the minimum confidence value for a detected entity to be returned.
2. Remove unnecessary PII recognizers, if the dataset does not contain these entities.
3. Update/replace the logic of specific recognizers to better suit a specific dataset or use case.
4. Replace PII recognizers with those coming from 3rd party services.

Every PII identification logic would have its errors, and there is a trade-off between false positives (falsely detected text) and false negatives (PII entities which are not detected).

## How can I evaluate the performance of my Presidio instance?

In addition to Presidio, we maintain a repo focused on evaluation of models and PII recognizers [here](https://github.com/microsoft/presidio-research). It also features a simple PII data generator.

## Does Presidio work on structured/tabular data?

This is an area we are actively looking into. We have an [example implementation](https://microsoft.github.io/presidio/samples/python/batch_processing/) of using Presidio on structured/semi-structured data. Also see the different discussions on this topic on the [Discussions](https://github.com/microsoft/presidio/discussions) section. If you have a question, suggestion, or a contribution in this area, please reach out by opening an issue, starting a discussion or reaching us directly at presidio@microsoft.com

## Can Presidio be used for Pseudonymization?

Pseudonymization is a de-identification technique in which the real data is replaced with fake data. Since there are various ways and approaches for this, we provide a simple [sample](https://microsoft.github.io/presidio/samples/python/example_custom_lambda_anonymizer/) which can be extended for more sophisticated usage. If you have a question or a request on this topic, please open an issue on the repo.

## How can I deploy Presidio into my environment?

The main Presidio modules (analyzer, anonymizer, image-redactor) can be used both as a Python package and as a dockerized REST API. See the [different deployment samples](https://microsoft.github.io/presidio/samples/) for example deployments.

## How can I contribute to Presidio?

First, review the [contribution guidelines](https://github.com/microsoft/presidio/blob/main/CONTRIBUTING.md), and feel free to reach out by opening and issue, posting a discussion or emailing us at presidio@microsoft.com
