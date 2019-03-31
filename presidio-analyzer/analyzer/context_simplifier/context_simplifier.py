from abc import abstractmethod


class ContextSimplifier:
    """ ContextSimplifier is responsible for preprocessing the context text
        before the different recognizers use the context to get better
        confidence on the score
    """

    def __init__(self):
        pass

    @abstractmethod
    def simplify(self, context):
        """ simplifiy the given context and return a simpler version
        """
