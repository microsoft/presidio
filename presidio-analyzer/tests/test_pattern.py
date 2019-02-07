from unittest import TestCase

from analyzer import Pattern


class TestPattern(TestCase):

    def test_to_dict(self):
        expected = {"name": "my pattern", "pattern": "[pat]", "strength": 0.9}
        pat = Pattern(name="my pattern",strength=0.9,pattern="[pat]")
        actual = pat.to_dict()

        assert expected == actual

    def test_from_dict(self):
        expected = {"name": "my pattern", "pattern": "[pat]", "strength": 0.9}
        pat = Pattern.from_dict(expected)
        actual = pat.to_dict()

        assert expected == actual
