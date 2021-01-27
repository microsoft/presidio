import json


class ErrorResponse:
    """
    Error Response for the Flask API.

    :param msg - the error message to return
    """

    def __init__(self, msg: str):
        self.error = msg

    def to_json(self) -> str:
        """Return a json string serializing this instance."""
        return json.dumps(self, default=lambda x: x.__dict__)
