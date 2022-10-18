
# spaCy/Stanza NLP engine

Presidio can be loaded with pre-trained or custom models coming from spaCy or Stanza.

## Using a public pre-trained spaCy/Stanza model

To replace the default model with a different public model, first download the desired spaCy/Stanza NER models.

- To download a new model with spaCy:

    ```sh
    python -m spacy download es_core_news_md
    ```

    In this example we download the medium size model for Spanish.

- To download a new model with Stanza:

    <!--pytest-codeblocks:skip-->
    ```python
    import stanza
    stanza.download("en") # where en is the language code of the model.
    ```

For the available models, follow these links: [spaCy](https://spacy.io/usage/models), [stanza](https://stanfordnlp.github.io/stanza/available_models.html#available-ner-models).

!!! tip "Tip"
    For Person, Location and Organization detection, it could be useful to try out the transformers based models (e.g. `en_core_web_trf`) which uses a more modern deep-learning architecture, but is generally slower than the default `en_core_web_lg` model.

## Training your own model

!!! note "Note"
    A labeled dataset containing text and labeled PII entities is required for training a new model.

For more information on model training and evaluation for Presidio, see the [Presidio-Research Github repository](https://github.com/microsoft/presidio-research).

To train your own model, see these links on spaCy and Stanza:

- [Train your own spaCy model](https://spacy.io/usage/training).
- [Train your own Stanza model](https://stanfordnlp.github.io/stanza/training.html).

Once models are trained, they should be installed locally in the same environment as Presidio Analyzer.

