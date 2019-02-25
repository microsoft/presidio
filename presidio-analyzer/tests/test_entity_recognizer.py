from unittest import TestCase

from analyzer import EntityRecognizer

LANGUAGE = "en"


class TestEntityRecognizer(TestCase):

    def test_to_dict_correct_dictionary(self):
        ent_recognizer = EntityRecognizer(["ENTITY"])
        entity_rec_dict = ent_recognizer.to_dict()
        
        assert entity_rec_dict is not None
        assert entity_rec_dict['supported_entities'] == ['ENTITY']
        assert entity_rec_dict['supported_language'] == 'en'

    def test_from_dict_returns_instance(self):
        ent_rec_dict = {"supported_entities": ["A", "B", "C"],
                        "supported_language": "he"
                        }
        entity_rec = EntityRecognizer.from_dict(ent_rec_dict)

        assert entity_rec.supported_entities == ["A", "B", "C"]
        assert entity_rec.supported_language == "he"
        assert entity_rec.version == "0.0.1"
