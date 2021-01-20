from flask import Flask, request

from presidio_anonymizer.anonymizer_engine import AnonymizerEngine
from presidio_anonymizer.entities.engine_request import AnonymizerEngineRequest
from presidio_anonymizer.entities.invalid_exception import InvalidParamException

app = Flask(__name__)


@app.route("/anonymize", methods=["POST"])
def anonymize():
    content = request.get_json()
    if not content:
        return "Invalid request json", 400
    try:
        data = AnonymizerEngineRequest(content)
    except InvalidParamException as e:
        return e.err, 400
    except Exception:
        # TODO add logger 2652
        return "Internal server error", 500
    text = AnonymizerEngine().anonymize(data)
    return text


if __name__ == "main":
    app.run()
