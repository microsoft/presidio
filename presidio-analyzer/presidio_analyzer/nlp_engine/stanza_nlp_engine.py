import logging
import warnings
from typing import Dict, List, Optional, Union

try:
    import stanza
    from stanza import Pipeline
    from stanza.models.common.pretrain import Pretrain
    from stanza.models.common.vocab import UNK_ID
    from stanza.resources.common import DEFAULT_MODEL_DIR

except ImportError:
    stanza = None


from spacy import Language, blank
from spacy.tokens import Doc, Token
from spacy.util import registry

from presidio_analyzer.nlp_engine import NerModelConfiguration, SpacyNlpEngine

logger = logging.getLogger("presidio-analyzer")


class StanzaNlpEngine(SpacyNlpEngine):
    """
    StanzaNlpEngine is an abstraction layer over the nlp module.

    It provides processing functionality as well as other queries
    on tokens.
    The StanzaNlpEngine uses spacy-stanza and stanza as its NLP module

    :param models: Dictionary with the name of the spaCy model per language.
    For example: models = [{"lang_code": "en", "model_name": "en"}]
    :param ner_model_configuration: Parameters for the NER model.
    See conf/stanza.yaml for an example

    """

    engine_name = "stanza"
    is_available = bool(stanza)

    def __init__(
        self,
        models: Optional[List[Dict[str, str]]] = None,
        ner_model_configuration: Optional[NerModelConfiguration] = None,
        download_if_missing: bool = True,
    ):
        super().__init__(models, ner_model_configuration)
        self.download_if_missing = download_if_missing

    def load(self) -> None:
        """Load the NLP model."""

        logger.debug(f"Loading Stanza models: {self.models}")

        self.nlp = {}
        for model in self.models:
            self._validate_model_params(model)
            self.nlp[model["lang_code"]] = load_pipeline(
                model["model_name"],
                processors="tokenize,pos,lemma,ner",
                download_method="DOWNLOAD_RESOURCES"
                if self.download_if_missing
                else None,
            )


# Code taken from https://github.com/explosion/spacy-stanza
# Supports Stanza > 1.7.0
def load_pipeline(
    name: str,
    *,
    lang: str = "",
    dir: Optional[str] = None,  # noqa
    package: str = "default",
    processors: Union[dict, str] = None,
    logging_level: Optional[Union[int, str]] = None,
    verbose: Optional[bool] = None,
    use_gpu: bool = True,
    **kwargs,
) -> Language:
    """Create a blank nlp object for a given language code.

    with a stanza pipeline as part of the tokenizer.

    To use the default stanza pipeline with
    the same language code, leave the tokenizer config empty. Otherwise, pass
    in the stanza pipeline settings in config["nlp"]["tokenizer"].

    name (str): The language code, e.g. "en".
    lang: str = "",
    dir: Optional[str] = None,
    package: str = "default",
    processors: Union[dict, str] = {},
    logging_level: Optional[Union[int, str]] = None,
    verbose: Optional[bool] = None,
    use_gpu: bool = True,
    **kwargs: Options for the individual stanza processors.
    RETURNS (Language): The nlp object.
    """

    if not processors:
        processors = {}

    # Create an empty config skeleton
    config = {"nlp": {"tokenizer": {"kwargs": {}}}}
    if lang == "":
        lang = name
    # Set the stanza tokenizer
    config["nlp"]["tokenizer"]["@tokenizers"] = "PipelineAsTokenizer.v1"
    # Set the stanza options
    config["nlp"]["tokenizer"]["lang"] = lang
    config["nlp"]["tokenizer"]["dir"] = dir
    config["nlp"]["tokenizer"]["package"] = package
    config["nlp"]["tokenizer"]["processors"] = processors
    config["nlp"]["tokenizer"]["logging_level"] = logging_level
    config["nlp"]["tokenizer"]["verbose"] = verbose
    config["nlp"]["tokenizer"]["use_gpu"] = use_gpu
    config["nlp"]["tokenizer"]["kwargs"].update(kwargs)
    return blank(name, config=config)


@registry.tokenizers("PipelineAsTokenizer.v1")
def create_tokenizer(
    lang: str = "",
    dir: Optional[str] = None,  # noqa
    package: str = "default",
    processors: Union[dict, str] = None,
    logging_level: Optional[Union[int, str]] = None,
    verbose: Optional[bool] = None,
    use_gpu: bool = True,
    kwargs: dict = None,
):
    """Create a tokenizer factory for a given language code.

    :param lang: The language code, e.g. "en".
    :param dir: The model directory.
    :param package: The model package.
    :param processors: The processors to use.
    :param logging_level: The logging level.
    :param verbose: Whether to be verbose.
    :param use_gpu: Whether to use the GPU.
    :param kwargs: Additional keyword arguments.
    """
    if not processors:
        processors = {}
    if not kwargs:
        kwargs = {}

    def tokenizer_factory(
        nlp,
        lang=lang,  # noqa
        dir=dir,  # noqa
        package=package,  # noqa
        processors=processors,  # noqa
        logging_level=logging_level,  # noqa
        verbose=verbose,  # noqa
        use_gpu=use_gpu,  # noqa
        kwargs=kwargs,  # noqa
    ) -> StanzaTokenizer:
        if dir is None:
            dir = DEFAULT_MODEL_DIR  # noqa
        snlp = Pipeline(
            lang=lang,
            dir=dir,
            package=package,
            processors=processors,
            logging_level=logging_level,
            verbose=verbose,
            use_gpu=use_gpu,
            **kwargs,
        )
        return StanzaTokenizer(
            snlp,
            nlp.vocab,
        )

    return tokenizer_factory


# Code taken from https://github.com/explosion/spacy-stanza
# Supports Stanza > 1.7.0
class StanzaTokenizer(object):
    """The entire stanza pipeline in a custom tokenizer.

    Because we're only running the Stanza pipeline once and don't split
    it up into spaCy pipeline components, we'll set all the attributes within
    a custom tokenizer.
    """

    def __init__(self, snlp, vocab):
        """Initialize the tokenizer.

        snlp (stanza.Pipeline): The initialized Stanza pipeline.
        vocab (spacy.vocab.Vocab): The vocabulary to use.
        RETURNS (Tokenizer): The custom tokenizer.
        """
        self.snlp = snlp
        self.vocab = vocab
        self.svecs = self._find_embeddings(snlp)

    def __call__(self, text):
        """Convert a Stanza Doc to a spaCy Doc.

        text (Unicode): The text to process.
        RETURNS (spacy.tokens.Doc): The spaCy Doc object.
        """
        if not text:
            return Doc(self.vocab)
        elif text.isspace():
            return Doc(self.vocab, words=[text], spaces=[False])

        snlp_doc = self.snlp(text)
        text = snlp_doc.text
        snlp_tokens, snlp_heads = self.__get_tokens_with_heads(snlp_doc)
        pos = []
        tags = []
        morphs = []
        deps = []
        heads = []
        lemmas = []
        token_texts = [t.text for t in snlp_tokens]
        is_aligned = True
        try:
            words, spaces = self.__get_words_and_spaces(token_texts, text)
        except ValueError:
            words = token_texts
            spaces = [True] * len(words)
            is_aligned = False
            warnings.warn(
                "Due to multiword token expansion or an alignment "
                "issue, the original text has been replaced by space-separated "
                "expanded tokens.",
                stacklevel=4,
            )
        offset = 0
        for i, word in enumerate(words):
            if word.isspace() and (
                i + offset >= len(snlp_tokens) or word != snlp_tokens[i + offset].text
            ):
                # insert a space token
                pos.append("SPACE")
                tags.append("_SP")
                morphs.append("")
                deps.append("")
                lemmas.append(word)

                # increment any heads left of this position that point beyond
                # this position to the right (already present in heads)
                for j in range(0, len(heads)):
                    if j + heads[j] >= i:
                        heads[j] += 1

                # decrement any heads right of this position that point beyond
                # this position to the left (yet to be added from snlp_heads)
                for j in range(i + offset, len(snlp_heads)):
                    if j + snlp_heads[j] < i + offset:
                        snlp_heads[j] -= 1

                # initial space tokens are attached to the following token,
                # otherwise attach to the preceding token
                if i == 0:
                    heads.append(1)
                else:
                    heads.append(-1)

                offset -= 1
            else:
                token = snlp_tokens[i + offset]
                assert word == token.text

                pos.append(token.upos or "")
                tags.append(token.xpos or token.upos or "")
                morphs.append(token.feats or "")
                deps.append(token.deprel or "")
                heads.append(snlp_heads[i + offset])
                lemmas.append(token.lemma or "")

        doc = Doc(
            self.vocab,
            words=words,
            spaces=spaces,
            pos=pos,
            tags=tags,
            morphs=morphs,
            lemmas=lemmas,
            deps=deps,
            heads=[head + i for i, head in enumerate(heads)],
        )
        ents = []
        for ent in snlp_doc.entities:
            ent_span = doc.char_span(ent.start_char, ent.end_char, ent.type)
            ents.append(ent_span)
        if not is_aligned or not all(ents):
            warnings.warn(
                f"Can't set named entities because of multi-word token "
                f"expansion or because the character offsets don't map to "
                f"valid tokens produced by the Stanza tokenizer:\n"
                f"Words: {words}\n"
                f"Entities: {[(e.text, e.type, e.start_char, e.end_char) for e in snlp_doc.entities]}", # noqa
                stacklevel=4,
            )
        else:
            doc.ents = ents

        if self.svecs is not None:
            doc.user_token_hooks["vector"] = self.token_vector
            doc.user_token_hooks["has_vector"] = self.token_has_vector
        return doc

    def pipe(self, texts):
        """Tokenize a stream of texts.

        texts: A sequence of Unicode texts.
        YIELDS (Doc): A sequence of Doc objects, in order.
        """
        for text in texts:
            yield self(text)

    @staticmethod
    def __get_tokens_with_heads(snlp_doc):
        """Flatten the tokens in the Stanza Doc and extract the token indices.

        extract the token indices of the sentence start tokens to set is_sent_start.

        snlp_doc (stanza.Document): The processed Stanza doc.
        RETURNS (list): The tokens (words).
        """
        tokens = []
        heads = []
        offset = 0
        for sentence in snlp_doc.sentences:
            for token in sentence.tokens:
                for word in token.words:
                    # Here, we're calculating the absolute token index in the doc,
                    # then the *relative* index of the head, -1 for zero-indexed
                    # and if the governor is 0 (root), we leave it at 0
                    if word.head:
                        head = word.head + offset - len(tokens) - 1
                    else:
                        head = 0
                    heads.append(head)
                    tokens.append(word)
            offset += sum(len(token.words) for token in sentence.tokens)
        return tokens, heads

    @staticmethod
    def __get_words_and_spaces(words, text):
        if "".join("".join(words).split()) != "".join(text.split()):
            raise ValueError("Unable to align mismatched text and words.")
        text_words = []
        text_spaces = []
        text_pos = 0
        # normalize words to remove all whitespace tokens
        norm_words = [word for word in words if not word.isspace()]
        # align words with text
        for word in norm_words:
            try:
                word_start = text[text_pos:].index(word)
            except ValueError:
                raise ValueError("Unable to align mismatched text and words.")
            if word_start > 0:
                text_words.append(text[text_pos : text_pos + word_start])
                text_spaces.append(False)
                text_pos += word_start
            text_words.append(word)
            text_spaces.append(False)
            text_pos += len(word)
            if text_pos < len(text) and text[text_pos] == " ":
                text_spaces[-1] = True
                text_pos += 1
        if text_pos < len(text):
            text_words.append(text[text_pos:])
            text_spaces.append(False)
        return text_words, text_spaces

    def token_vector(self, token:Token):
        """Get Stanza's pretrained word embedding for given token.

        :param token: The token whose embedding will be returned
        :return (np.ndarray[ndim=1, dtype='float32']): the embedding/vector.
            token.vector.size > 0 if Stanza pipeline contains a processor with
            embeddings, else token.vector.size == 0.
            A 0-vector (origin) will be returned
        when the token doesn't exist in snlp's pretrained embeddings.
        """
        unit_id = self.svecs.vocab.unit2id(token.text)
        return self.svecs.emb[unit_id]

    def token_has_vector(self, token):
        """Check if the token exists as a unit in snlp's pretrained embeddings."""
        return self.svecs.vocab.unit2id(token.text) != UNK_ID

    @staticmethod
    def _find_embeddings(snlp):
        """Find pretrained word embeddings in any of a SNLP's processors.

        RETURNS (Pretrain): Or None if no embeddings were found.
        """
        embs = None
        for proc in snlp.processors.values():
            if hasattr(proc, "pretrain") and isinstance(proc.pretrain, Pretrain):
                embs = proc.pretrain
                break
        return embs

    # dummy serialization methods
    def to_bytes(self, **kwargs):  # noqa
        return b""

    def from_bytes(self, _bytes_data, **kwargs):  # noqa
        return self

    def to_disk(self, _path, **kwargs):  # noqa
        return None

    def from_disk(self, _path, **kwargs):  # noqa
        return self
