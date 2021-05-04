"""Exception to indicate the request we received is invalid."""


class InvalidParamException(Exception):
    """Throw exception with error when user input is not valid.

    param msg: Message to be added to the exception
    """

    def __init__(self, msg: str):
        self.err_msg = msg
        super().__init__(self.err_msg)
