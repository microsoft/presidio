"""REST API server for image anonymizer."""
import logging
import os

from flask import Flask, request

DEFAULT_PORT = "3000"


class Server:
    """Flask server for image anonymizer."""

    def __init__(self):
        self.logger = logging.getLogger("presidio-image-anonymizer")
        self.app = Flask(__name__)

        @self.app.route("/health")
        def health() -> str:
            """Return basic health probe result.  get ok + 200."""
            return "ok"

        @self.app.route("/anonymize", methods=["POST"])
        def anonymize():
            content = request.get_json()
            return content


if __name__ == "__main__":
    port = int(os.environ.get("PORT", DEFAULT_PORT))
    server = Server()
    server.app.run(host="0.0.0.0", port=port)
