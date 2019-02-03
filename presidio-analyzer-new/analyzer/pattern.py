

class Pattern:

    def __init__(self, name, strength, pattern):
        """
        A class that represents a regex pattern.
        :param name: the name of the pattern
        :param strength: the pattern's strength (values varies 0-1)
        :param pattern: the regex pattern to detect
        """
        self.name = name
        self.strength = strength
        self.pattern = pattern

