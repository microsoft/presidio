"""Exception to indicate the request json we received is invalid"""


class InvalidJsonException(Exception):
    def __init__(self, err: str):
        self.err = err
        super().__init__(self.err)
