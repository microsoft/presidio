import copy
import logging
from pathlib import Path
from typing import Optional, List, Iterable, Union, Type, Dict
from presidio_analyzer.nlp_engine.transformers_nlp_engine import (
    TransformersNlpEngine,
)

import yaml

from presidio_analyzer import EntityRecognizer, PatternRecognizer
from presidio_analyzer.nlp_engine import NlpEngine, SpacyNlpEngine, StanzaNlpEngine
from presidio_analyzer.predefined_recognizers import (
    CreditCardRecognizer,
    CryptoRecognizer,
    DateRecognizer,
    EmailRecognizer,
    IbanRecognizer,
    IpRecognizer,
    MedicalLicenseRecognizer,
    NhsRecognizer,
    PhoneRecognizer,
    UrlRecognizer,
    UsBankRecognizer,
    UsLicenseRecognizer,
    UsItinRecognizer,
    UsPassportRecognizer,
    UsSsnRecognizer,
    SgFinRecognizer,
    SpacyRecognizer,
    EsNifRecognizer,
    StanzaRecognizer,
    AuAbnRecognizer,
    AuAcnRecognizer,
    AuTfnRecognizer,
    AuMedicareRecognizer,
    ItDriverLicenseRecognizer,
    ItFiscalCodeRecognizer,
    ItVatCodeRecognizer,
    TransformersRecognizer,
    ItPassportRecognizer,
    ItIdentityCardRecognizer,
)

logger = logging.getLogger("presidio-analyzer")


class RecognizerRegistry:
    """
    Detect, register and hold all recognizers to be used by the analyzer.

    :param recognizers: An optional list of recognizers,
    that will be available instead of the predefined recognizers
    """

    def __init__(self, recognizers: Optional[Iterable[EntityRecognizer]] = None):

        if recognizers:
            self.recognizers = recognizers
        else:
            self.recognizers = []

    def load_predefined_recognizers(
        self, languages: Optional[List[str]] = None, nlp_engine: NlpEngine = None
    ) -> None:
        """
        Load the existing recognizers into memory.

        :param languages: List of languages for which to load recognizers
        :param nlp_engine: The NLP engine to use.
        :return: None
        """
        if not languages:
            languages = ["en"]

        nlp_recognizer = self._get_nlp_recognizer(nlp_engine)
        recognizers_map = {
            "en": [
                UsBankRecognizer,
                UsLicenseRecognizer,
                UsItinRecognizer,
                UsPassportRecognizer,
                UsSsnRecognizer,
                NhsRecognizer,
                SgFinRecognizer,
                AuAbnRecognizer,
                AuAcnRecognizer,
                AuTfnRecognizer,
                AuMedicareRecognizer,
            ],
            "es": [EsNifRecognizer],
            "it": [
                ItDriverLicenseRecognizer,
                ItFiscalCodeRecognizer,
                ItVatCodeRecognizer,
                ItIdentityCardRecognizer,
                ItPassportRecognizer,
            ],
            "ALL": [
                CreditCardRecognizer,
                CryptoRecognizer,
                DateRecognizer,
                EmailRecognizer,
                IbanRecognizer,
                IpRecognizer,
                MedicalLicenseRecognizer,
                nlp_recognizer,
                PhoneRecognizer,
                UrlRecognizer,
            ],
        }
        for lang in languages:
            lang_recognizers = [rc() for rc in recognizers_map.get(lang, [])]
            self.recognizers.extend(lang_recognizers)
            all_recognizers = [
                rc(supported_language=lang) for rc in recognizers_map.get("ALL", [])
            ]
            self.recognizers.extend(all_recognizers)

    @staticmethod
    def _get_nlp_recognizer(
        nlp_engine: NlpEngine,
    ) -> Union[Type[SpacyRecognizer], Type[StanzaRecognizer]]:
        """Return the recognizer leveraging the selected NLP Engine."""

        if not nlp_engine or type(nlp_engine) == SpacyNlpEngine:
            return SpacyRecognizer
        if isinstance(nlp_engine, StanzaNlpEngine):
            return StanzaRecognizer
        if isinstance(nlp_engine, TransformersNlpEngine):
            return TransformersRecognizer
        else:
            logger.warning(
                "nlp engine should be either SpacyNlpEngine,"
                "StanzaNlpEngine or TransformersNlpEngine"
            )
            # Returning default
            return SpacyRecognizer

    def get_recognizers(
        self,
        language: str,
        entities: Optional[List[str]] = None,
        all_fields: bool = False,
        ad_hoc_recognizers: Optional[List[EntityRecognizer]] = None,
    ) -> List[EntityRecognizer]:
        """
        Return a list of recognizers which supports the specified name and language.

        :param entities: the requested entities
        :param language: the requested language
        :param all_fields: a flag to return all fields of a requested language.
        :param ad_hoc_recognizers: Additional recognizers provided by the user
        as part of the request
        :return: A list of the recognizers which supports the supplied entities
        and language
        """
        if language is None:
            raise ValueError("No language provided")

        if entities is None and all_fields is False:
            raise ValueError("No entities provided")

        all_possible_recognizers = copy.copy(self.recognizers)
        if ad_hoc_recognizers:
            all_possible_recognizers.extend(ad_hoc_recognizers)

        # filter out unwanted recognizers
        to_return = set()
        if all_fields:
            to_return = [
                rec
                for rec in all_possible_recognizers
                if language == rec.supported_language
            ]
        else:
            for entity in entities:
                subset = [
                    rec
                    for rec in all_possible_recognizers
                    if entity in rec.supported_entities
                    and language == rec.supported_language
                ]

                if not subset:
                    logger.warning(
                        "Entity %s doesn't have the corresponding"
                        " recognizer in language : %s",
                        entity,
                        language,
                    )
                else:
                    to_return.update(set(subset))

        logger.debug(
            "Returning a total of %s recognizers",
            str(len(to_return)),
        )

        if not to_return:
            raise ValueError("No matching recognizers were found to serve the request.")

        return list(to_return)

    def add_recognizer(self, recognizer: EntityRecognizer) -> None:
        """
        Add a new recognizer to the list of recognizers.

        :param recognizer: Recognizer to add
        """
        if not isinstance(recognizer, EntityRecognizer):
            raise ValueError("Input is not of type EntityRecognizer")

        self.recognizers.append(recognizer)

    def remove_recognizer(self, recognizer_name: str) -> None:
        """
        Remove a recognizer based on its name.

        :param recognizer_name: Name of recognizer to remove
        """
        new_recognizers = [
            rec for rec in self.recognizers if rec.name != recognizer_name
        ]
        logger.info(
            "Removed %s recognizers which had the name %s",
            str(len(self.recognizers) - len(new_recognizers)),
            recognizer_name,
        )
        self.recognizers = new_recognizers

    def add_pattern_recognizer_from_dict(self, recognizer_dict: Dict):
        """
        Load a pattern recognizer from a Dict into the recognizer registry.

        :param recognizer_dict: Dict holding a serialization of an PatternRecognizer

        :example:
        >>> registry = RecognizerRegistry()
        >>> recognizer = { "name": "Titles Recognizer", "supported_language": "de","supported_entity": "TITLE", "deny_list": ["Mr.","Mrs."]} # noqa: E501
        >>> registry.add_pattern_recognizer_from_dict(recognizer)
        """

        recognizer = PatternRecognizer.from_dict(recognizer_dict)
        self.add_recognizer(recognizer)

    def add_recognizers_from_yaml(self, yml_path: Union[str, Path]):
        r"""
        Read YAML file and load recognizers into the recognizer registry.

        See example yaml file here:
        https://github.com/microsoft/presidio/blob/main/presidio-analyzer/conf/example_recognizers.yaml

        :example:
        >>> yaml_file = "recognizers.yaml"
        >>> registry = RecognizerRegistry()
        >>> registry.add_recognizers_from_yaml(yaml_file)

        """

        try:
            with open(yml_path, "r") as stream:
                yaml_recognizers = yaml.safe_load(stream)

            for yaml_recognizer in yaml_recognizers["recognizers"]:
                self.add_pattern_recognizer_from_dict(yaml_recognizer)
        except IOError as io_error:
            print(f"Error reading file {yml_path}")
            raise io_error
        except yaml.YAMLError as yaml_error:
            print(f"Failed to parse file {yml_path}")
            raise yaml_error
        except TypeError as yaml_error:
            print(f"Failed to parse file {yml_path}")
            raise yaml_error
