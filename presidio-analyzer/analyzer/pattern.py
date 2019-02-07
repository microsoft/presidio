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


    def to_dict(self):
        """
        Turns this instance into a dictionary
        :return: a dictionary
        """

        return_dict = {"name": self.name,
                       "strength": self.strength,
                       "pattern": self.pattern
                       }
        return return_dict

    @classmethod
    def from_dict(cls, pattern_dict):
        """
        Loads an instance from a dictionary
        :param pattern_dict: a dictionary holding the pattern's parameters
        :return: a Pattern instance
        """
        return cls(**pattern_dict)
