from unittest import TestCase

from analyzer import Pattern
my_pattern = Pattern(name="my pattern", score=0.9, regex="[re]")
my_pattern_dict = {"name": "my pattern", "regex": "[re]", "score": 0.9}


class TestPattern(TestCase):

    def test_to_dict(self):
        expected = my_pattern_dict
        actual = my_pattern.to_dict()

        assert expected == actual

    def test_from_dict(self):
        expected = my_pattern
        actual = Pattern.from_dict(my_pattern_dict)

        assert expected.name == actual.name
        assert expected.score == actual.score
        assert expected.regex == actual.regex
