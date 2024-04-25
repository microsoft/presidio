"""REST API server for image redactor."""
import base64
import logging
import os
from io import BytesIO

from PIL import Image
from flask import Flask, request, jsonify, Response
from presidio_analyzer import AnalyzerEngineProvider

from presidio_image_redactor import ImageAnalyzerEngine, ImageRedactorEngine
from presidio_image_redactor.entities import InvalidParamException
from presidio_image_redactor.entities.api_request_convertor import (
    get_json_data,
    image_to_byte_array,
    color_fill_string_to_value,
)

DEFAULT_PORT = "3000"

WELCOME_MESSAGE = r"""
 _______  _______  _______  _______ _________ ______  _________ _______
(  ____ )(  ____ )(  ____ \(  ____ \\__   __/(  __  \ \__   __/(  ___  )
| (    )|| (    )|| (    \/| (    \/   ) (   | (  \  )   ) (   | (   ) |
| (____)|| (____)|| (__    | (_____    | |   | |   ) |   | |   | |   | |
|  _____)|     __)|  __)   (_____  )   | |   | |   | |   | |   | |   | |
| (      | (\ (   | (            ) |   | |   | |   ) |   | |   | |   | |
| )      | ) \ \__| (____/\/\____) |___) (___| (__/  )___) (___| (___) |
|/       |/   \__/(_______/\_______)\_______/(______/ \_______/(_______)
"""


class Server:
    """Flask server for image redactor."""

    def __init__(self):
        self.logger = logging.getLogger("presidio-image-redactor")
        self.app = Flask(__name__)
        self.logger.info("Starting image redactor engine")

        image_analyzer = self.__create_image_analyzer_engine()
        self.engine = ImageRedactorEngine(image_analyzer_engine=image_analyzer)
        self.logger.info(WELCOME_MESSAGE)

        @self.app.route("/health")
        def health() -> str:
            """Return basic health probe result."""
            return "Presidio Image Redactor service is up"

        @self.app.route("/redact", methods=["POST"])
        def redact():
            """Return a redacted image."""
            params = get_json_data(request.form.get("data"))
            color_fill = color_fill_string_to_value(params)
            if request.get_json(silent=True) and "image" in request.json:
                im = Image.open(BytesIO(base64.b64decode(request.json.get("image"))))
                analyzer_entities = request.json.get('analyzer_entities')
                redacted_image = self.engine.redact(im, color_fill,
                                                    entities=analyzer_entities)
                img_byte_arr = image_to_byte_array(redacted_image, im.format)
                return Response(base64.b64encode(img_byte_arr),
                                mimetype="application/octet-stream")

            elif request.files and "image" in request.files:
                im = Image.open(request.files.get("image"))
                redacted_image = self.engine.redact(im, color_fill, score_threshold=0.4)
                img_byte_arr = image_to_byte_array(redacted_image, im.format)
                return Response(img_byte_arr,
                                mimetype="application/octet-stream")
            else:
                raise InvalidParamException("Invalid parameter, please add image data")

        @self.app.errorhandler(InvalidParamException)
        def invalid_param(err):
            self.logger.warning(
                f"failed to redact image with validation error: {err.err_msg}"
            )
            return jsonify(error=err.err_msg), 422

        @self.app.errorhandler(Exception)
        def server_error(e):
            self.logger.error(f"A fatal error occurred during execution: {e}")
            return jsonify(error="Internal server error"), 500

    @staticmethod
    def __create_image_analyzer_engine() -> ImageAnalyzerEngine:
        analyzer_conf_file = os.environ.get("ANALYZER_CONF_FILE")
        nlp_engine_conf_file = os.environ.get("NLP_ENGINE_CONF_FILE")
        recognizer_registry_conf_file = os.environ.get("RECOGNIZER_REGISTRY_CONF_FILE")

        test_analyzer = AnalyzerEngineProvider(
            analyzer_engine_conf_file=analyzer_conf_file,
            nlp_engine_conf_file=nlp_engine_conf_file,
            recognizer_registry_conf_file=recognizer_registry_conf_file,
        ).create_engine()

        return ImageAnalyzerEngine(analyzer_engine=test_analyzer)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", DEFAULT_PORT))
    server = Server()
    server.app.run(host="0.0.0.0", port=port)
