class Pattern:

    def __init__(self, name, pattern, strength):
        """
        A class that represents a regex pattern.
        :param name: the name of the pattern
        :param pattern: the regex pattern to detect
        :param strength: the pattern's strength (values varies 0-1)
        """
        self.name = name
        self.pattern = pattern
        self.strength = strength

