"""Handle a serializable error response."""
import json


class ErrorResponse:
    """
    Error Response.

    :param msg - the error message to return
    """

    def __init__(self, msg):
        self.error = msg

    def to_json(self) -> str:
        """Return a json string serializing this instance."""
        return json.dumps(self, default=lambda x: x.__dict__)
