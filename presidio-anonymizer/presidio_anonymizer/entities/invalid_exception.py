"""Exception to indicate the request we received is invalid."""


class InvalidParamException(Exception):
    """Throw exception with error when user input is not valid."""

    def __init__(self, err: str):
        self.err = err
        super().__init__(self.err)
